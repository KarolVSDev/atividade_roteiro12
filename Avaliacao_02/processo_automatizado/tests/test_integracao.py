import pytest
from processo4.contrato import validar_entrada, ContratoInvalido

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