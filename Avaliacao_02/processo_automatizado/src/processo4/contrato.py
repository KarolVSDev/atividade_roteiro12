"""
Contrato de integração entre Processo 3 (Cadastro) e Processo 4 (SAC).

Formato esperado do arquivo .json que o Processo 3 deposita em
`entrada_processo3/` (um arquivo por solicitação):

{
    "protocolo": "string, identificador único da solicitação",
    "status_cadastro": "sucesso" | "erro",
    "cliente": {
        "nome": "string",
        "email": "string",
        "cpf": "string"
    },
    "motivo_erro": "string, obrigatório quando status_cadastro == 'erro'",
    "duplicado": true | false   (opcional, default false)
}

Este módulo faz apenas a validação estrutural mínima. Regras de
negócio de cadastro (duplicidade, validação de CPF etc.) são
responsabilidade do Processo 3.
"""

CAMPOS_OBRIGATORIOS_CLIENTE = ("nome", "email")


class ContratoInvalido(Exception):
    pass


def validar_entrada(dados):
    """
    Valida a estrutura mínima do resultado recebido do Processo 3.
    Lança ContratoInvalido com uma mensagem clara quando algo
    obrigatório está ausente ou mal formado.
    """

    if not isinstance(dados, dict):
        raise ContratoInvalido("Arquivo de entrada não é um objeto JSON.")

    protocolo = dados.get("protocolo")
    if not protocolo:
        raise ContratoInvalido("Campo obrigatório ausente: 'protocolo'.")

    status_cadastro = dados.get("status_cadastro")
    if status_cadastro not in ("sucesso", "erro"):
        raise ContratoInvalido(
            "Campo 'status_cadastro' deve ser 'sucesso' ou 'erro' "
            f"(recebido: {status_cadastro!r})."
        )

    cliente = dados.get("cliente")
    if not isinstance(cliente, dict):
        raise ContratoInvalido("Campo obrigatório ausente: 'cliente'.")

    for campo in CAMPOS_OBRIGATORIOS_CLIENTE:
        if not cliente.get(campo):
            raise ContratoInvalido(
                f"Campo obrigatório ausente em 'cliente': '{campo}'."
            )

    if status_cadastro == "erro" and not dados.get("motivo_erro"):
        raise ContratoInvalido(
            "Quando 'status_cadastro' é 'erro', o campo "
            "'motivo_erro' é obrigatório."
        )

    return True


def montar_saida_processo5(
    protocolo,
    cliente,
    status_cadastro,
    status_atendimento,
    acao_realizada,
    data_atendimento,
    observacoes=""
):
    """
    Monta o dicionário no formato entregue ao Processo 5.
    """

    return {
        "protocolo": protocolo,
        "cliente": cliente,
        "status_cadastro": status_cadastro,
        "status_atendimento": status_atendimento,
        "acao_realizada": acao_realizada,
        "data_atendimento": data_atendimento,
        "observacoes": observacoes,
    }
