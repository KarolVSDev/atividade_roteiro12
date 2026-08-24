import pytest
from processo4.contrato import validar_entrada, ContratoInvalido
from processo5.relatorios import calcular_metricas

#python -m pytest

def test_integracao_processo3_para_processo4_sucesso():
    """Simula a integração: Processo 3 envia dados com sucesso para o Processo 4 validar."""
    pacote_processo3 = {
        "protocolo": "20260818150000",
        "status_cadastro": "sucesso",
        "cliente": {
            "nome": "Ana Karoline",
            "email": "anakaroline.souza@ifam.edu.br",
            "cpf": "04880588210"
        }
    }
    
    resultado = validar_entrada(pacote_processo3)
    assert resultado is True

def test_integracao_processo3_para_processo4_erro_com_motivo():
    """Simula a integração em caso de falha: Processo 3 envia erro e o Processo 4 exige o motivo."""
    pacote_erro_processo3 = {
        "protocolo": "20260818150001",
        "status_cadastro": "erro",
        "cliente": {
            "nome": "Ana Karoline",
            "email": "anakaroline.souza@ifam.edu.br",
            "cpf": "04880588210"
        },
        "motivo_erro": "Falha simulada no navegador do Portal Fake"
    }
    
    assert validar_entrada(pacote_erro_processo3) is True

def test_integracao_rejeita_erro_sem_motivo():
    """Garante que se o Processo 3 mandar um erro sem a chave 'motivo_erro', a integração rejeita."""
    pacote_invalido = {
        "protocolo": "20260818150002",
        "status_cadastro": "erro",
        "cliente": {
            "nome": "Ana Karoline",
            "email": "anakaroline.souza@ifam.edu.br",
            "cpf": "04880588210"
        }
    }
    
    with pytest.raises(ContratoInvalido):
        validar_entrada(pacote_invalido)

def test_integracao_rejeita_status_desconhecido():
    """Garante que o Processo 4 rejeita se o status não for nem 'sucesso' nem 'erro'."""
    pacote_status_maluco = {
        "protocolo": "20260818150003",
        "status_cadastro": "talvez",  # Status inválido pelo contrato
        "cliente": {
            "nome": "Ana Karoline",
            "email": "anakaroline.souza@ifam.edu.br",
            "cpf": "04880588210"
        }
    }
    
    with pytest.raises(ContratoInvalido):
        validar_entrada(pacote_status_maluco)


def test_integracao_fluxo_pont_a_ponta():
    """Simula o fluxo integrado de ponta a ponta: do contrato do Processo 4 até as métricas do Processo 5."""
    
    # 1. Simula o formato exato que o Processo 5 espera ler
    lote_atendimentos = [
        {
            "protocolo": "20260824100001",
            "status": "sucesso",  # Ajustado para a chave que o Processo 5 lê
            "cliente": {"nome": "Ana Karoline", "email": "ana@email.com", "cpf": "12345678901"}
        },
        {
            "protocolo": "20260824100002",
            "status": "erro",     # Ajustado para a chave que o Processo 5 lê
            "motivo_erro": "Elemento não encontrado no Portal Fake",
            "cliente": {"nome": "Teste da Silva", "email": "teste@email.com", "cpf": "98765432109"}
        }
    ]
    
    # 2. Processo 5 consome esses dados consolidados para gerar as métricas gerenciais
    metricas = calcular_metricas(lote_atendimentos)
    
    # 3. Valida se a integração entre o SAC e os Relatórios aconteceu corretamente
    assert metricas["total_processado"] == 2
    assert metricas["taxa_sucesso_percentual"] == 50.0