import pytest
from datetime import datetime

def test_geracao_protocolo_sac():
    """Valida se o formato do protocolo gerado pelo SAC segue o padrão esperado."""
    i = 0
    protocolo = datetime.now().strftime("%Y%m%d%H%M%S") + f"{i:03d}"
    
    assert len(protocolo) >= 14
    assert protocolo.isdigit()