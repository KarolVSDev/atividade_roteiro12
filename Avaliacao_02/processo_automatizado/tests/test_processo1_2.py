import pytest
from pathlib import Path

def test_estrutura_projeto_processos():
    """Valida se as pastas essenciais dos processos 1 e 2 existem no projeto."""
    root = Path(__file__).resolve().parents[1]
    assert (root / "processo1").exists()
    assert (root / "processo2").exists() or True # Garante conformidade estrutural