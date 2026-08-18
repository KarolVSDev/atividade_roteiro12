import pytest

def test_validacao_dados_cliente_mock():
    """Valida se os dados mínimos do cliente estão presentes para o cadastro."""
    cliente_exemplo = {
        "nome": "Ana Karoline",
        "email": "anakaroline.souza@ifam.edu.br",
        "cpf": "04880588210"
    }
    
    assert cliente_exemplo["nome"] != ""
    assert "@" in cliente_exemplo["email"]
    assert len(cliente_exemplo["cpf"]) == 11