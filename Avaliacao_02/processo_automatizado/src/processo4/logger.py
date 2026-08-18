import logging

from src.processo4.config import ARQUIVO_LOG_TEXTO


def configurar_logger():

    logger = logging.getLogger("processo4_sac")

    if logger.handlers:
        # Evita duplicar handlers caso configurar_logger()
        # seja chamado mais de uma vez no mesmo processo.
        return logger

    logger.setLevel(logging.INFO)

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formato)

    handler_arquivo = logging.FileHandler(
        ARQUIVO_LOG_TEXTO,
        encoding="utf-8"
    )
    handler_arquivo.setFormatter(formato)

    logger.addHandler(handler_console)
    logger.addHandler(handler_arquivo)

    return logger


logger = configurar_logger()
