from pathlib import Path

from processo5.relatorios import calcular_metricas, executar_processo5


REGISTROS = [
    {
        "id_cliente": "C001",
        "status": "sucesso",
        "duracao_segundos": 2,
        "mensagem": "Atendimento concluído",
        "erro": None,
    },
    {
        "id_cliente": "C002",
        "status": "falha",
        "duracao_segundos": 4,
        "mensagem": "Falha na integração",
        "erro": "Timeout",
    },
    {
        "id_cliente": "C003",
        "status": "pendente",
        "duracao_segundos": 3,
        "mensagem": "Aguardando retorno",
        "erro": None,
    },
]


def test_calcula_metricas_principais():
    metricas = calcular_metricas(REGISTROS)

    assert metricas["total_processado"] == 3
    assert metricas["sucessos"] == 1
    assert metricas["falhas"] == 1
    assert metricas["pendencias"] == 1
    assert metricas["taxa_sucesso_percentual"] == 33.33
    assert metricas["duracao_media_segundos"] == 3.0


def test_lista_vazia_nao_divide_por_zero():
    metricas = calcular_metricas([])

    assert metricas["total_processado"] == 0
    assert metricas["taxa_sucesso_percentual"] == 0.0
    assert metricas["duracao_media_segundos"] is None


def test_gera_artefatos_e_incrementa_versao(tmp_path: Path):
    saidas = tmp_path / "saidas"
    logs = tmp_path / "logs"

    primeira_execucao = executar_processo5(REGISTROS, saidas, logs)
    segunda_execucao = executar_processo5(REGISTROS, saidas, logs)

    assert primeira_execucao["versao"] == "v001"
    assert segunda_execucao["versao"] == "v002"
    assert Path(primeira_execucao["arquivos"]["json"]).exists()
    assert Path(primeira_execucao["arquivos"]["csv"]).exists()
    assert Path(primeira_execucao["arquivos"]["manifesto"]).exists()
    assert Path(primeira_execucao["arquivos"]["log"]).exists()
