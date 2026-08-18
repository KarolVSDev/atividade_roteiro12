import os
import csv
import smtplib
import logging
import json
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# ============================================================
# CONFIGURAÇÕES E CAMINHOS
# ============================================================
APP_ROOT = Path(__file__).resolve().parents[1]

# Pasta de evidências (CSV)
PASTA_EVIDENCIAS = APP_ROOT / "evidencias"
PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
ARQUIVO_LOG_ATENDIMENTOS = PASTA_EVIDENCIAS / "atendimentos_sac.csv"

# NOVA PASTA DA SUA COLEGA PARA OS JSONs
PASTA_SAIDA_PROCESSO5 = APP_ROOT / "saida_processo5"
PASTA_SAIDA_PROCESSO5.mkdir(parents=True, exist_ok=True)

# Carrega credenciais do Processo 1/2
ENV_PATH = APP_ROOT / ".env"
load_dotenv(ENV_PATH)
EMAIL = os.getenv("EMAIL") or os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP") or os.getenv("EMAIL_SENHA")

# ============================================================
# FUNÇÕES DE COMUNICAÇÃO
# ============================================================
def _enviar(destinatario, assunto, corpo):
    if not EMAIL or not SENHA_APP:
        raise Exception("Credenciais de e-mail não configuradas no .env")
        
    mensagem = MIMEMultipart()
    mensagem["From"] = EMAIL
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    try:
        servidor.starttls()
        servidor.login(EMAIL, SENHA_APP)
        servidor.send_message(mensagem)
    finally:
        servidor.quit()

def notificar_cadastro_aprovado(nome_cliente, email_cliente, protocolo):
    assunto = f"Atendimento concluído - Cadastro aprovado (Prot: {protocolo})"
    corpo = f"""Olá, {nome_cliente}!

Seu cadastro (protocolo {protocolo}) foi concluído com sucesso.
Nossa equipe de atendimento confirma o processamento da sua solicitação.

Atenciosamente,
Equipe SAC - Portal Fake
"""
    try:
        _enviar(email_cliente, assunto, corpo)
        logging.info(f"[{protocolo}] E-mail de sucesso enviado para {email_cliente}.")
        return True
    except Exception as erro:
        logging.error(f"[{protocolo}] Falha ao enviar e-mail de sucesso: {erro}")
        return False

def notificar_cadastro_com_erro(nome_cliente, email_cliente, protocolo, motivo_erro):
    assunto = f"Atendimento - Pendência no seu cadastro (Prot: {protocolo})"
    corpo = f"""Olá, {nome_cliente}!

Identificamos uma pendência no processamento do seu cadastro (protocolo {protocolo}).

Motivo: {motivo_erro}

Nossa equipe técnica já está ciente. 
Responda este e-mail caso precise de ajuda.

Atenciosamente,
Equipe SAC - Portal Fake
"""
    try:
        _enviar(email_cliente, assunto, corpo)
        logging.info(f"[{protocolo}] E-mail de pendência enviado para {email_cliente}.")
        return True
    except Exception as erro:
        logging.error(f"[{protocolo}] Falha ao enviar e-mail de pendência: {erro}")
        return False

# ============================================================
# FUNÇÕES DE ATENDIMENTO E REGISTRO
# ============================================================
def registrar_atendimento(protocolo, cliente, status_cadastro, comunicacao_enviada, status_atendimento, observacoes=""):
    arquivo_novo = not ARQUIVO_LOG_ATENDIMENTOS.exists()
    cabecalho = [
        "data_hora", "protocolo", "cliente_nome", "cliente_email", 
        "status_cadastro", "comunicacao_enviada", "status_atendimento", "observacoes"
    ]
    
    try:
        with open(ARQUIVO_LOG_ATENDIMENTOS, mode="a", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            if arquivo_novo:
                escritor.writerow(cabecalho)
            
            escritor.writerow([
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                protocolo,
                cliente.get("nome", ""),
                cliente.get("email", ""),
                status_cadastro,
                "sim" if comunicacao_enviada else "nao",
                status_atendimento,
                observacoes,
            ])
    except Exception as erro:
        logging.error(f"[{protocolo}] Falha ao registrar atendimento no CSV: {erro}")

def executar_sac(dados_clientes):
    """
    Função principal chamada pelo pai.bot.py
    """
    logging.info("--- Iniciando Processo 4: SAC ---")
    
    if not dados_clientes:
        logging.warning("Nenhum dado recebido para o SAC.")
        return []

    resultados_sac = []
    
    for i, cliente in enumerate(dados_clientes):
        # 1. Gera um protocolo único (AnoMesDiaHoraMinSeg + numero do cliente)
        protocolo = datetime.now().strftime("%Y%m%d%H%M%S") + f"{i:03d}"
        cliente["protocolo"] = protocolo
        
        nome = cliente.get("nome", "Cliente")
        email_cliente = cliente.get("email", "")
        status_cadastro = cliente.get("status_cadastro", "Erro")
        
        logging.info(f"[{protocolo}] Verificando resultado do cadastro de {nome}: {status_cadastro}.")
        
        # 2. Roteia a comunicação baseado no resultado do Processo 3
        if status_cadastro == "Sucesso":
            comunicacao_ok = notificar_cadastro_aprovado(nome, email_cliente, protocolo)
            status_atendimento = "concluido" if comunicacao_ok else "concluido_sem_notificacao"
            observacoes = "" if comunicacao_ok else "Cadastro aprovado, mas falhou envio do e-mail."
        else:
            motivo_erro = cliente.get("detalhe_erro", "Erro desconhecido na automação.")
            comunicacao_ok = notificar_cadastro_com_erro(nome, email_cliente, protocolo, motivo_erro)
            status_atendimento = "encerrado_com_pendencia" if comunicacao_ok else "falha_comunicacao"
            observacoes = motivo_erro if comunicacao_ok else f"{motivo_erro} | Falha adicional: e-mail não enviado."
            
        # 3. Registra na base do SAC (CSV da colega)
        registrar_atendimento(protocolo, cliente, status_cadastro, comunicacao_ok, status_atendimento, observacoes)
        
        # 4. Enriquece o dicionário para entregar ao Processo 5 (Gerencial)
        cliente["status_atendimento"] = status_atendimento
        cliente["observacoes_sac"] = observacoes
        
        # 5. SALVA O .JSON DA SUA COLEGA
        caminho_json = PASTA_SAIDA_PROCESSO5 / f"{protocolo}.json"
        try:
            with open(caminho_json, "w", encoding="utf-8") as arquivo:
                json.dump(cliente, arquivo, ensure_ascii=False, indent=2)
            logging.info(f"[{protocolo}] Arquivo JSON salvo com sucesso: {caminho_json.name}")
        except Exception as e:
            logging.error(f"[{protocolo}] Falha ao salvar JSON: {e}")
            
        resultados_sac.append(cliente)
        
    logging.info(f"Processo 4 concluído. Atendimentos registrados: {len(resultados_sac)}")
    return resultados_sac