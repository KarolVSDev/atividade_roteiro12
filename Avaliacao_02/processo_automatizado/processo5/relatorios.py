import logging
import json
from datetime import datetime

def gerar_relatorio(dados_finais):
    """
    Consolida os dados, gera métricas e salva o relatório.
    """
    logging.info("--- Iniciando Processo 5: Relatórios e Gerência ---")
    
    if not dados_finais:
        logging.error("Nenhum dado recebido para consolidar.")
        return

    total_processado = len(dados_finais)
    sucessos = 0
    erros = 0

    # Consolidação e Geração de Métricas
    for cliente in dados_finais:
        if cliente.get('status_cadastro') == 'Sucesso':
            sucessos += 1
        else:
            erros += 1

    taxa_sucesso = (sucessos / total_processado) * 100 if total_processado > 0 else 0

    logging.info("=== RESULTADOS CONSOLIDADOS ===")
    logging.info(f"Total Processado: {total_processado}")
    logging.info(f"Sucessos: {sucessos}")
    logging.info(f"Erros: {erros}")
    logging.info(f"Taxa de Sucesso: {taxa_sucesso:.2f}%")

    # Versionamento dos resultados (Salvando em um arquivo JSON com timestamp)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_execucao_{timestamp}.json"

    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump({
                "metricas": {
                    "total": total_processado,
                    "sucessos": sucessos,
                    "erros": erros,
                    "taxa_sucesso": taxa_sucesso
                },
                "detalhes": dados_finais
            }, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Relatório gerencial salvo com sucesso: {nome_arquivo}")
    except Exception as e:
        logging.error(f"Falha ao salvar o relatório gerencial: {e}")

    logging.info("--- Processo 5 Concluído ---")