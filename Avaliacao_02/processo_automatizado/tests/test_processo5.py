import pytest
from pathlib import Path
from processo5.relatorios import calcular_metricas

def test_calcula_metricas_vazias():
    """Garante que listas vazias não gerem erro de divisão por zero."""
    metricas = calcular_metricas([])
    assert metricas["total_processado"] == 0
    assert metricas["taxa_sucesso_percentual"] == 0.0