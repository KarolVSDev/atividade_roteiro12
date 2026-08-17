import sys
import os

# Adiciona o diretorio raiz ao sys.path para garantir a importacao
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from processo3.cadastro import cadastrar_cliente, verificar_duplicidade

def test_sucesso_cadastro():
    cliente = {
        "Nome": "Carlos Lima",
        "CPF": "55544433322",
        "Data de Nascimento": "10/05/1995",
        "Endereço": "Rua 10, Manaus/AM",
        "E-mail": "carlos@email.com",
        "Telefone": "(92) 98888-1111"
    }
    res = cadastrar_cliente(cliente)
    assert res["status"] == "SUCESSO"
    assert res["motivo"] == "Cadastro realizado com sucesso."

def test_duplicidade_cadastro():
    cliente = {
        "Nome": "Cliente Repetido",
        "CPF": "11122233344",
        "Data de Nascimento": "01/01/1990",
        "Endereço": "Av. Principal, 100",
        "E-mail": "repetido@email.com",
        "Telefone": "(92) 99999-0000"
    }
    res = cadastrar_cliente(cliente)
    assert res["status"] == "DUPLICADO"

def test_dados_incompletos():
    cliente = {"Nome": "", "CPF": "", "Data de Nascimento": "", "Endereço": ""}
    res = cadastrar_cliente(cliente)
    assert res["status"] == "ERRO_DADOS"

def test_verificar_duplicidade():
    assert verificar_duplicidade("111.222.333-44") is True
    assert verificar_duplicidade("999.888.777-66") is True
    assert verificar_duplicidade("000.111.222-33") is False
