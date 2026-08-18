"""Implementação do Processo 5.
Este módulo recebe os resultados do Processo 4, consolida os dados, 
calcula indicadores e gera relatórios versionados em JSON e CSV.
"""

from __future__ import annotations
import csv
import hashlib
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping

# --- Constantes de Status ---
STATUS_SUCESSO = {"sucesso", "success", "ok", "concluido", "concluído"}
STATUS_FALHA = {"falha", "erro", "error", "failed", "fracasso"}
STATUS_PENDENTE = {"pendente", "pending", "em_analise", "em análise", "aguardando"}

def _agora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)

def _configurar_logger(diretorio_logs: Path) -> logging.Logger:
    diretorio_logs.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("processo5")
    logger.setLevel(logging.INFO)
    
    # Limpa handlers existentes para evitar duplicação em execuções sucessivas
    if logger.hasHandlers():
        logger.handlers.clear()

    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
    caminho_log = diretorio_logs / "processo5.log"
    
    arquivo_handler = logging.FileHandler(caminho_log, encoding="utf-8")
    arquivo_handler.setFormatter(formato)
    logger.addHandler(arquivo_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)
    logger.addHandler(console_handler)

    return logger

def normalizar_registro(registro: Mapping[str, Any]) -> dict[str, Any]:
    resultado = dict(registro)
    resultado["id_cliente"] = str(registro.get("id_cliente", registro.get("cliente_id", registro.get("id", "N/A"))))
    resultado["status"] = str(registro.get("status", "desconhecido")).strip().lower()
    resultado["duracao_segundos"] = _numero_ou_none(registro.get("duracao_segundos", 0))
    resultado["mensagem"] = str(registro.get("mensagem", ""))
    return resultado

def _numero_ou_none(valor: Any) -> float | None:
    try:
        return float(valor) if valor is not None else None
    except (TypeError, ValueError):
        return None

def _classificar_status(status: str) -> str:
    s = status.strip().lower()
    if s in STATUS_SUCESSO: return "sucesso"
    if s in STATUS_FALHA: return "falha"
    if s in STATUS_PENDENTE: return "pendente"
    return "outros"

def calcular_metricas(registros: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    normalizados = [normalizar_registro(registro) for registro in registros]
    total = len(normalizados)
    classificacoes = Counter(_classificar_status(item["status"]) for item in normalizados)
    duracoes = [item["duracao_segundos"] for item in normalizados if item["duracao_segundos"] is not None]

    sucessos = classificacoes["sucesso"]
    taxa_sucesso = round((sucessos / total) * 100, 2) if total else 0.0

    return {
        "total_processado": total,
        "sucessos": sucessos,
        "falhas": classificacoes["falha"],
        "pendencias": classificacoes["pendente"],
        "taxa_sucesso_percentual": taxa_sucesso,
        "duracao_media_segundos": round(mean(duracoes), 3) if duracoes else 0.0,
    }

def _proxima_versao(diretorio_saidas: Path) -> int:
    maior_versao = 0
    for caminho in diretorio_saidas.glob("relatorio_v*.json"):
        try:
            numero = int(caminho.stem.split("v")[1])
            maior_versao = max(maior_versao, numero)
        except (ValueError, IndexError):
            continue
    return maior_versao + 1

def _sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()

def _gravar_csv(caminho: Path, registros: list[dict[str, Any]]) -> None:
    campos = ["id_cliente", "status", "duracao_segundos", "mensagem"]
    with caminho.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(registros)

def gerar_relatorio(registros: Iterable[Mapping[str, Any]], saidas: Path, logs: Path) -> dict[str, Any]:
    saidas.mkdir(parents=True, exist_ok=True)
    logger = _configurar_logger(logs)
    inicio = time.perf_counter()

    normalizados = [normalizar_registro(r) for r in registros]
    metricas = calcular_metricas(normalizados)
    
    versao = f"v{_proxima_versao(saidas):03d}"
    caminho_json = saidas / f"relatorio_{versao}.json"
    caminho_csv = saidas / f"relatorio_{versao}.csv"

    # Salvar JSON
    relatorio = {"versao": versao, "gerado_em": _agora_utc().isoformat(), "metricas": metricas, "registros": normalizados}
    caminho_json.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Salvar CSV
    _gravar_csv(caminho_csv, normalizados)

    logger.info(f"Relatório {versao} gerado com sucesso em {time.perf_counter() - inicio:.2f}s")
    return {"versao": versao, "metricas": metricas, "json": str(caminho_json), "csv": str(caminho_csv)}

def executar_processo5(dados, diretorio_saidas="processo5/saidas", diretorio_logs="processo5/logs"):
    return gerar_relatorio(dados, Path(diretorio_saidas), Path(diretorio_logs))