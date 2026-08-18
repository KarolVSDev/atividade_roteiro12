from .main import processar_resultado_cadastro
from .config import PASTA_ENTRADA_PROCESSO3
import json

def executar_sac(dados_clientes):
    """
    Ponte para manter a lógica original
    """
    resultados = []
    for cliente_dict in dados_clientes:
        protocolo = cliente_dict.get("protocolo", "PROT000")
        caminho_temp = PASTA_ENTRADA_PROCESSO3 / f"{protocolo}.json"
        
        with open(caminho_temp, "w", encoding="utf-8") as f:
            json.dump(cliente_dict, f, ensure_ascii=False)
            
        saida = processar_resultado_cadastro(cliente_dict)
        resultados.append(saida)
        
    return resultados