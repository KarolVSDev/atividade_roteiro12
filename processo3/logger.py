import logging
import os

def setup_logger(name: str = "Processo3_Cadastro") -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | [%(levelname)s] | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler("logs/processo3.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
