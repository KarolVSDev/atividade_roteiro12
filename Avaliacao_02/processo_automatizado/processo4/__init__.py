from .main import processar_resultado_cadastro
from .config import PASTA_ENTRADA_PROCESSO3
from datetime import datetime
import json

def executar_sac(dados_clientes):
    """
    Ponte de compatibilidade para integrar a lista em memória do bot.py
    com a lógica modular oficial do Processo 4.
    """
    resultados = []
    for i, cliente_dict in enumerate(dados_clientes):
        # 1. Garante a criação do protocolo se ele ainda não existir
        if not cliente_dict.get("protocolo"):
            protocolo = datetime.now().strftime("%Y%m%d%H%M%S") + f"{i:03d}"
            cliente_dict["protocolo"] = protocolo
        else:
            protocolo = cliente_dict["protocolo"]

        cliente_dict["id_cliente"] = cliente_dict.get("cpf") or protocolo
            
        # 2. Normaliza o status_cadastro para minúsculo
        if "status_cadastro" in cliente_dict:
            cliente_dict["status_cadastro"] = str(cliente_dict["status_cadastro"]).lower()
            
        # 3. Garante que o objeto "cliente" exista estruturado para atender ao contrato.py
        if "cliente" not in cliente_dict or not isinstance(cliente_dict["cliente"], dict):
            cliente_dict["cliente"] = {
                "nome": cliente_dict.get("nome", "Cliente"),
                "email": cliente_dict.get("email", ""),
                "cpf": cliente_dict.get("cpf", "")
            }
            
        caminho_temp = PASTA_ENTRADA_PROCESSO3 / f"{protocolo}.json"
        
        with open(caminho_temp, "w", encoding="utf-8") as f:
            json.dump(cliente_dict, f, ensure_ascii=False)
            
        saida = processar_resultado_cadastro(cliente_dict)
        resultados.append(saida)
        
    return resultados