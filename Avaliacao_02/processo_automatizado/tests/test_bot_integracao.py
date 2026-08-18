import pytest
from pathlib import Path

def test_existencia_arquivo_principal():
    """Garante que o arquivo principal do bot existe na raiz."""
    root = Path(__file__).resolve().parents[1]
    bot_path = root / "bot.py"
    assert bot_path.exists(), "O arquivo principal pai.bot.py não foi encontrado!"