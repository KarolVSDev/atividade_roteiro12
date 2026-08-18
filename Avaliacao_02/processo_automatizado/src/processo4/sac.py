import json

from datetime import datetime

from src.processo4.contrato import (
    ContratoInvalido,
    validar_entrada,
    montar_saida_processo5,
)
from src.processo4.comunicacao import (
    notificar_cadastro_aprovado,
    notificar_cadastro_com_erro,
)
from src.processo4.atendimento import registrar_atendimento
from src.processo4.config import PASTA_SAIDA_PROCESSO5
from src.processo4.logger import logger


def processar_resultado_cadastro(dados):
    """
    Recebe o dicionário já lido do arquivo entregue pelo Processo 3,
    executa o atendimento (SAC) e devolve o dicionário que será
    salvo para o Processo 5.

    Lança ContratoInvalido se os dados não seguirem o contrato
    combinado com o Processo 3.
    """

    validar_entrada(dados)

    protocolo = dados["protocolo"]
    cliente = dados["cliente"]
    status_cadastro = dados["status_cadastro"]

    logger.info(f"[{protocolo}] Verificando resultado do cadastro: {status_cadastro}.")

    # ========================================================
    # TRATAMENTO DE SUCESSO
    # ========================================================
    if status_cadastro == "sucesso":

        comunicacao_ok = notificar_cadastro_aprovado(
            cliente["nome"],
            cliente["email"],
            protocolo,
        )

        status_atendimento = "concluido" if comunicacao_ok else "concluido_sem_notificacao"

        observacoes = (
            "" if comunicacao_ok
            else "Cadastro aprovado, mas falhou o envio do e-mail ao cliente."
        )

    # ========================================================
    # TRATAMENTO DE ERRO
    # ========================================================
    else:

        motivo_erro = dados["motivo_erro"]

        comunicacao_ok = notificar_cadastro_com_erro(
            cliente["nome"],
            cliente["email"],
            protocolo,
            motivo_erro,
        )

        status_atendimento = "encerrado_com_pendencia" if comunicacao_ok else "falha_comunicacao"

        observacoes = motivo_erro if comunicacao_ok else (
            f"{motivo_erro} | Falha adicional: não foi possível notificar o cliente."
        )

    registrar_atendimento(
        protocolo=protocolo,
        cliente=cliente,
        status_cadastro=status_cadastro,
        comunicacao_enviada=comunicacao_ok,
        status_atendimento=status_atendimento,
        observacoes=observacoes,
    )

    saida = montar_saida_processo5(
        protocolo=protocolo,
        cliente=cliente,
        status_cadastro=status_cadastro,
        status_atendimento=status_atendimento,
        acao_realizada="notificacao_cliente" if comunicacao_ok else "notificacao_pendente",
        data_atendimento=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        observacoes=observacoes,
    )

    return saida


def enviar_para_processo5(protocolo, saida):
    """
    Salva o resultado do atendimento na pasta de saída do Processo 5.
    """

    caminho_saida = PASTA_SAIDA_PROCESSO5 / f"{protocolo}.json"

    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        json.dump(saida, arquivo, ensure_ascii=False, indent=2)

    logger.info(f"[{protocolo}] Resultado encaminhado ao Processo 5: {caminho_saida.name}.")
