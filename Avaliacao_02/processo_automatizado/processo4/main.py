from pathlib import Path
import json
import shutil
import sys

APP_ROOT = Path(__file__).resolve().parents[2]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# from src.processo4.config import (
#     PASTA_ENTRADA_PROCESSO3,
#     PASTA_PROCESSADO,
#     PASTA_ERRO,
# )
# from src.processo4.contrato import ContratoInvalido
# from src.processo4.sac import processar_resultado_cadastro, enviar_para_processo5
# from src.processo4.logger import logger
from .config import (
    PASTA_ENTRADA_PROCESSO3,
    PASTA_PROCESSADO,
    PASTA_ERRO,
)
from .contrato import ContratoInvalido
from .sac import processar_resultado_cadastro, enviar_para_processo5
from .logger import logger


def processar_arquivo(caminho_arquivo):

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

    except (json.JSONDecodeError, OSError) as erro:
        logger.error(f"Arquivo ilegível ({caminho_arquivo.name}): {erro}")
        shutil.move(str(caminho_arquivo), str(PASTA_ERRO / caminho_arquivo.name))
        return

    try:
        saida = processar_resultado_cadastro(dados)
        enviar_para_processo5(saida["protocolo"], saida)

        shutil.move(str(caminho_arquivo), str(PASTA_PROCESSADO / caminho_arquivo.name))

    except ContratoInvalido as erro:
        logger.error(f"Contrato inválido em {caminho_arquivo.name}: {erro}")
        shutil.move(str(caminho_arquivo), str(PASTA_ERRO / caminho_arquivo.name))

    except Exception as erro:
        # Falha inesperada: não deixa o dado seguir incompleto para o
        # Processo 5, registra para análise (fallback) e segue o lote.
        logger.exception(f"Falha inesperada ao processar {caminho_arquivo.name}: {erro}")
        shutil.move(str(caminho_arquivo), str(PASTA_ERRO / caminho_arquivo.name))


def processar_solicitacoes():

    arquivos = sorted(PASTA_ENTRADA_PROCESSO3.glob("*.json"))

    if not arquivos:
        logger.info("Nenhuma solicitação pendente em entrada_processo3/.")
        return

    logger.info(f"{len(arquivos)} solicitação(ões) encontrada(s) para atendimento.")

    for caminho_arquivo in arquivos:
        processar_arquivo(caminho_arquivo)


def main():
    logger.info("Iniciando Processo 4 - SAC...")
    processar_solicitacoes()
    logger.info("Processo 4 - SAC finalizado.")


if __name__ == "__main__":
    main()