import sys
import logging
from pathlib import Path

# 1. A CONFIGURAÇÃO DE LOGS DEVE SER A PRIMEIRA COISA DO ARQUIVO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automacao.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 2. Garante que o Python encontre as pastas dos processos
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 3. Importação dos processos
from processo1.email_monitor import processar_emails
from processo3.cadastro import executar_cadastro
# from processo4.sac import executar_sac
from processo4 import executar_sac
from processo5.relatorios import gerar_relatorio

def main():
    logging.info("=== Iniciando Solução de Hyperautomation ===")
    try:
        logging.info("Iniciando Processos 1 e 2: Monitoramento e Planilha")
        
        dados_extraidos = processar_emails() 
        
        if not dados_extraidos:
            logging.warning("Nenhum cliente novo foi processado ou extraído nesta execução.")
            logging.info("=== Processo Concluído (Sem novas demandas) ===")
            sys.exit(0) 

        logging.info("Iniciando Processo 3: Cadastro")
        dados_p3 = executar_cadastro(dados_extraidos)
        
        logging.info("Iniciando Processo 4: SAC")
        dados_p4 = executar_sac(dados_p3)
        
        logging.info("Iniciando Processo 5: Relatórios e Gerência")
        
        # Ponte de dados: traduzimos o resultado do SAC para o formato que o Processo 5 exige
        # registros_para_p5 = []
        # for c in dados_p4:
        #     registros_para_p5.append({
        #         "id_cliente": c.get("cpf", "ID_DESCONHECIDO"), 
        #         "status": c.get("status_atendimento"),
        #         "duracao_segundos": 2.5,
        #         "mensagem": c.get("observacoes_sac", "Atendimento realizado"),
        #         "erro": c.get("detalhe_erro")
        #     })
        registros_para_p5 = []
        for c in dados_p4:
            # Tenta pegar o CPF da raiz, de dentro de 'cliente', ou usa o protocolo como fallback
            cliente_info = c.get("cliente", {})
            id_real = c.get("cpf") or cliente_info.get("cpf") or c.get("protocolo", "ID_DESCONHECIDO")
            
            registros_para_p5.append({
                "id_cliente": id_real, 
                "status": c.get("status_atendimento"),
                "duracao_segundos": 2.5,
                "mensagem": c.get("observacoes_sac", "Atendimento realizado"),
                "erro": c.get("detalhe_erro")
            })
        
        # Executa o relatório e salva em 'processo5/saidas'
        pasta_saidas = APP_ROOT / "processo5" / "saidas"
        pasta_logs_p5 = APP_ROOT / "processo5" / "logs"
        
        resultado_p5 = gerar_relatorio(
            registros=registros_para_p5, 
            saidas=pasta_saidas, 
            logs=pasta_logs_p5
        )
        
        logging.info(f"Relatório gerado com sucesso: {resultado_p5['json']}")
        logging.info("=== Processos 1 ao 5 Concluídos com Sucesso ===")
        
    except Exception as e:
        logging.error(f"FALHA CRÍTICA NA AUTOMAÇÃO: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()