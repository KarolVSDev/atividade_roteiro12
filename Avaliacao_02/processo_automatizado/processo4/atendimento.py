import csv

from datetime import datetime

from .config import ARQUIVO_LOG_ATENDIMENTOS
from .logger import logger
# from src.processo4.config import ARQUIVO_LOG_ATENDIMENTOS
# from src.processo4.logger import logger

CABECALHO = [
    "data_hora",
    "protocolo",
    "cliente_nome",
    "cliente_email",
    "status_cadastro",
    "comunicacao_enviada",
    "status_atendimento",
    "observacoes",
]


def registrar_atendimento(
    protocolo,
    cliente,
    status_cadastro,
    comunicacao_enviada,
    status_atendimento,
    observacoes=""
):
    """
    Registra uma linha no histórico de atendimentos (CSV).
    Falha aqui não deve interromper o fluxo do SAC: é registrada
    no log e o processamento segue (fallback).
    """

    arquivo_novo = not ARQUIVO_LOG_ATENDIMENTOS.exists()

    try:
        with open(
            ARQUIVO_LOG_ATENDIMENTOS,
            mode="a",
            newline="",
            encoding="utf-8"
        ) as arquivo:

            escritor = csv.writer(arquivo)

            if arquivo_novo:
                escritor.writerow(CABECALHO)

            escritor.writerow([
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                protocolo,
                cliente.get("nome", ""),
                cliente.get("email", ""),
                status_cadastro,
                "sim" if comunicacao_enviada else "nao",
                status_atendimento,
                observacoes,
            ])

        logger.info(f"[{protocolo}] Atendimento registrado em {ARQUIVO_LOG_ATENDIMENTOS.name}.")

    except Exception as erro:
        logger.error(f"[{protocolo}] Falha ao registrar atendimento em CSV: {erro}")