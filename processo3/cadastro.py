import os
from typing import Dict, Any, List
from .logger import setup_logger

logger = setup_logger()

BASE_CLIENTES_CADASTRADOS = {"11122233344", "99988877766"}

def verificar_duplicidade(cpf: str) -> bool:
    cpf_limpo = "".join(filter(str.isdigit, str(cpf)))
    return cpf_limpo in BASE_CLIENTES_CADASTRADOS

def acionar_fallback(cliente: Dict[str, Any], motivo: str) -> None:
    os.makedirs("processo3/fallback", exist_ok=True)
    caminho = "processo3/fallback/pendentes_reprocessamento.log"
    logger.warning(f"Fallback acionado para '{cliente.get('Nome', 'Desconhecido')}': {motivo}")
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(
            f"CPF: {cliente.get('CPF', '')} | "
            f"Nome: {cliente.get('Nome', '')} | "
            f"E-mail: {cliente.get('E-mail', '')} | "
            f"Motivo: {motivo}\n"
        )

def cadastrar_cliente(cliente: Dict[str, Any]) -> Dict[str, Any]:
    nome = str(cliente.get("Nome", "")).strip()
    cpf = str(cliente.get("CPF", "")).strip()
    data_nasc = str(cliente.get("Data de Nascimento", "")).strip()
    endereco = str(cliente.get("Endereço", "")).strip()

    if not nome or not cpf or not data_nasc or not endereco:
        motivo = "Dados cadastrais obrigatórios ausentes ou inválidos."
        logger.error(f"{motivo} | Cliente: '{nome}' | CPF: '{cpf}'")
        return {"status": "ERRO_DADOS", "motivo": motivo, "cliente": cliente}

    if verificar_duplicidade(cpf):
        motivo = f"CPF {cpf} já se encontra cadastrado no sistema."
        logger.warning(motivo)
        return {"status": "DUPLICADO", "motivo": motivo, "cliente": cliente}

    try:
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        BASE_CLIENTES_CADASTRADOS.add(cpf_limpo)
        logger.info(f"Cliente '{nome}' (CPF: {cpf}) cadastrado com sucesso!")
        return {"status": "SUCESSO", "motivo": "Cadastro realizado com sucesso.", "cliente": cliente}
    except Exception as e:
        motivo = f"Falha na integração com o sistema: {str(e)}"
        logger.error(motivo)
        acionar_fallback(cliente, motivo)
        return {"status": "FALHA_SISTEMA", "motivo": motivo, "cliente": cliente}

def executar_processo3(lista_clientes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logger.info(f"Iniciando Processo 3. Registros recebidos: {len(lista_clientes)}")
    resultados = []
    for cliente in lista_clientes:
        resultado = cadastrar_cliente(cliente)
        resultados.append(resultado)
    logger.info(f"Processo 3 concluído. {len(resultados)} cadastros processados.")
    return resultados
