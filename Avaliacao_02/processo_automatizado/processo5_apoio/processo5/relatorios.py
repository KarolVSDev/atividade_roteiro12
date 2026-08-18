"""Implementação de referência do Processo 5.

O módulo recebe os resultados do Processo 4, consolida os dados, calcula
indicadores, grava logs e gera relatórios versionados em JSON e CSV.
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


STATUS_SUCESSO = {"sucesso", "sucesso", "success", "ok", "concluido", "concluído"}
STATUS_FALHA = {"falha", "erro", "error", "failed", "fracasso"}
STATUS_PENDENTE = {"pendente", "pending", "em_analise", "em análise", "aguardando"}


def _agora_utc() -> datetime:
    """Retorna a data/hora atual em UTC, com precisão de segundos."""

    return datetime.now(timezone.utc).replace(microsecond=0)


def _configurar_logger(diretorio_logs: Path) -> logging.Logger:
    """Configura um logger próprio do Processo 5 sem duplicar handlers."""

    diretorio_logs.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("processo5")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    caminho_log = diretorio_logs / "processo5.log"
    caminho_resolvido = caminho_log.resolve()
    ja_configurado = any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename).resolve() == caminho_resolvido
        for handler in logger.handlers
    )

    if not ja_configurado:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        arquivo_handler = logging.FileHandler(caminho_log, encoding="utf-8")
        arquivo_handler.setFormatter(formato)
        logger.addHandler(arquivo_handler)

    return logger


def normalizar_registro(registro: Mapping[str, Any]) -> dict[str, Any]:
    """Padroniza um registro vindo do Processo 4.

    O Processo 4 pode usar nomes ligeiramente diferentes. Esta função mantém
    os campos originais e cria campos canônicos para o Processo 5.
    """

    resultado = dict(registro)
    resultado["id_cliente"] = str(
        registro.get("id_cliente", registro.get("cliente_id", registro.get("id", "")))
    )
    resultado["status"] = str(registro.get("status", "desconhecido")).strip().lower()
    resultado["duracao_segundos"] = _numero_ou_none(
        registro.get("duracao_segundos", registro.get("duracao", registro.get("tempo_segundos")))
    )
    resultado["mensagem"] = str(registro.get("mensagem", registro.get("message", "")))
    resultado["erro"] = registro.get("erro", registro.get("error"))
    return resultado


def _numero_ou_none(valor: Any) -> float | None:
    if valor is None or valor == "":
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if numero >= 0 else None


def _classificar_status(status: str) -> str:
    status_normalizado = status.strip().lower()
    if status_normalizado in STATUS_SUCESSO:
        return "sucesso"
    if status_normalizado in STATUS_FALHA:
        return "falha"
    if status_normalizado in STATUS_PENDENTE:
        return "pendente"
    return "outros"


def calcular_metricas(registros: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Calcula indicadores gerenciais sobre os resultados do Processo 4."""

    normalizados = [normalizar_registro(registro) for registro in registros]
    total = len(normalizados)
    classificacoes = Counter(_classificar_status(item["status"]) for item in normalizados)
    duracoes = [
        item["duracao_segundos"]
        for item in normalizados
        if item["duracao_segundos"] is not None
    ]

    sucessos = classificacoes["sucesso"]
    taxa_sucesso = round((sucessos / total) * 100, 2) if total else 0.0

    return {
        "total_processado": total,
        "sucessos": sucessos,
        "falhas": classificacoes["falha"],
        "pendencias": classificacoes["pendente"],
        "outros_status": classificacoes["outros"],
        "taxa_sucesso_percentual": taxa_sucesso,
        "duracao_media_segundos": round(mean(duracoes), 3) if duracoes else None,
        "duracao_total_segundos": round(sum(duracoes), 3) if duracoes else 0.0,
    }


def _proxima_versao(diretorio_saidas: Path) -> int:
    """Encontra a próxima versão sem sobrescrever relatórios anteriores."""

    maior_versao = 0
    for caminho in diretorio_saidas.glob("relatorio_v*.json"):
        try:
            numero = int(caminho.stem.removeprefix("relatorio_v"))
        except ValueError:
            continue
        maior_versao = max(maior_versao, numero)
    return maior_versao + 1


def _sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _gravar_csv(caminho: Path, registros: list[dict[str, Any]]) -> None:
    campos = ["id_cliente", "status", "duracao_segundos", "mensagem", "erro"]
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(registros)


def gerar_relatorio(
    registros: Iterable[Mapping[str, Any]],
    diretorio_saidas: str | Path = "processo5/saidas",
    diretorio_logs: str | Path = "processo5/logs",
) -> dict[str, Any]:
    """Gera e grava os artefatos do Processo 5.

    Retorna um dicionário com a versão, as métricas e os caminhos dos arquivos.
    """

    saidas = Path(diretorio_saidas)
    logs = Path(diretorio_logs)
    saidas.mkdir(parents=True, exist_ok=True)
    logger = _configurar_logger(logs)
    inicio = time.perf_counter()
    inicio_utc = _agora_utc()

    registros_normalizados = [normalizar_registro(registro) for registro in registros]
    metricas = calcular_metricas(registros_normalizados)
    versao_numero = _proxima_versao(saidas)
    versao = f"v{versao_numero:03d}"
    prefixo = f"relatorio_{versao}"

    logger.info("Iniciando consolidação do Processo 5")
    logger.info("Registros recebidos: %s", metricas["total_processado"])

    relatorio = {
        "processo": "Processo 5 - Relatórios e Gerência",
        "versao": versao,
        "gerado_em_utc": inicio_utc.isoformat(),
        "metricas": metricas,
        "registros": registros_normalizados,
    }

    caminho_json = saidas / f"{prefixo}.json"
    caminho_csv = saidas / f"{prefixo}.csv"
    caminho_manifesto = saidas / f"manifest_{versao}.json"

    caminho_json.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _gravar_csv(caminho_csv, registros_normalizados)

    manifesto = {
        "processo": "Processo 5 - Relatórios e Gerência",
        "versao": versao,
        "gerado_em_utc": inicio_utc.isoformat(),
        "arquivos": {
            caminho_json.name: {"sha256": _sha256(caminho_json)},
            caminho_csv.name: {"sha256": _sha256(caminho_csv)},
        },
    }
    caminho_manifesto.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    duracao_execucao = round(time.perf_counter() - inicio, 4)
    logger.info("Versão gerada: %s", versao)
    logger.info("Relatório JSON: %s", caminho_json)
    logger.info("Relatório CSV: %s", caminho_csv)
    logger.info("Execução concluída em %s segundos", duracao_execucao)

    return {
        "versao": versao,
        "metricas": metricas,
        "arquivos": {
            "json": str(caminho_json),
            "csv": str(caminho_csv),
            "manifesto": str(caminho_manifesto),
            "log": str(logs / "processo5.log"),
        },
        "duracao_execucao_segundos": duracao_execucao,
    }


def executar_processo5(
    resultado_processo4: Iterable[Mapping[str, Any]],
    diretorio_saidas: str | Path = "processo5/saidas",
    diretorio_logs: str | Path = "processo5/logs",
) -> dict[str, Any]:
    """Ponto de entrada usado pelo `pai.bot.py`."""

    logs = Path(diretorio_logs)
    logger = _configurar_logger(logs)
    try:
        return gerar_relatorio(resultado_processo4, diretorio_saidas, diretorio_logs)
    except Exception:
        logger.exception("Falha durante a execução do Processo 5")
        raise
