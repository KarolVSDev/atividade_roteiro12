import imaplib
import email as email_module
from email.header import decode_header
import os
import socket
from email.utils import parseaddr
from pathlib import Path
import sys
import logging # <--- ADICIONADO AQUI

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from processo2.preencher_planilha import processar_ficha_cadastral, extrair_dados_ficha
from processo2.envio_email import enviar_confirmacao, enviar_pendencia
from dotenv import load_dotenv

from processo2.drive import (
    autenticar_google_drive, upload_arquivo, criar_subpasta,
    mover_arquivo, PASTA_ENCAMINHADOS, PASTA_DOCUMENTOS_OK,
    PASTA_DRIVE_DOWNLOAD, PASTA_DOWNLOAD, PASTA_DOCUMENTOS_PENDENTES
)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

EMAIL = os.getenv("EMAIL") or os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP") or os.getenv("EMAIL_SENHA")

# logging.info(f"EMAIL carregado: {EMAIL}")
# logging.info(f"SENHA_APP carregada: {SENHA_APP is not None}")

PASTA_DRIVE_DOWNLOAD = "1dMZwGTF3X_45AgDZ2yd3dWO5TTlWhu3-"

def conectar_email():
    logging.info("Testando DNS...")
    ip = socket.gethostbyname("imap.gmail.com")
    logging.info(f"imap.gmail.com -> {ip}")
    logging.info("Conectando ao Gmail...")
    
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    logging.info("Realizando login...")
    mail.login(EMAIL, SENHA_APP)
    logging.info("Login realizado com sucesso!")
    return mail

def extrair_nome_cliente(remetente):
    nome, email = parseaddr(remetente)
    if nome: return nome.strip()
    return email.split("@")[0]

def decodificar_texto(texto):
    if not texto: 
        return ""
    if not isinstance(texto, (str, bytes)):
        texto = str(texto)
    
    try:
        partes = decode_header(texto)
        resultado = ""
        for valor, encoding in partes:
            if isinstance(valor, bytes):
                try:
                    resultado += valor.decode(encoding or "utf-8", errors="replace")
                except (UnicodeDecodeError, LookupError):
                    resultado += valor.decode("latin-1", errors="replace")
            else:
                resultado += str(valor) if valor else ""
        return resultado
    except Exception:
        return str(texto) if texto else ""

def documentacao_completa(lista_arquivos):
    encontrou_rg = encontrou_cpf = encontrou_comprovante = False
    for arquivo in lista_arquivos:
        nome = arquivo.lower()
        if "rg" in nome: encontrou_rg = True
        if "cpf" in nome: encontrou_cpf = True
        if "comprovante" in nome: encontrou_comprovante = True
    return encontrou_rg and encontrou_cpf and encontrou_comprovante

def documentos_faltantes(lista_arquivos):
    documentos = {"RG": False, "CPF": False, "COMPROVANTE DE RESIDENCIA": False}
    for arquivo in lista_arquivos:
        nome = arquivo.upper()
        if "RG" in nome: documentos["RG"] = True
        if "CPF" in nome: documentos["CPF"] = True
        if "COMPROVANTE" in nome or "RESIDENCIA" in nome:
            documentos["COMPROVANTE DE RESIDENCIA"] = True

    faltantes = [doc for doc, encontrado in documentos.items() if not encontrado]
    return faltantes

def baixar_anexos_pdf(mail):
    LIMITE_EMAILS = 10
    clientes_processados = []

    mail.select("INBOX")
    status, mensagens = mail.search(None, "UNSEEN")

    if status != "OK":
        logging.error("Erro ao buscar mensagens.")
        return clientes_processados

    ids_emails = mensagens[0].split()
    ids_emails = ids_emails[-LIMITE_EMAILS:]
    ids_emails.reverse()

    if not ids_emails:
        logging.info("Nenhum e-mail não lido encontrado.")
        return clientes_processados

    logging.info(f"{len(ids_emails)} e-mail(s) encontrados para processamento.")
    service = autenticar_google_drive()

    for email_id in ids_emails:
        status, dados = mail.fetch(email_id, "(RFC822)")
        if status != "OK": continue

        mensagem = email_module.message_from_bytes(dados[0][1])
        
        # Proteção contra assunto nulo ou vazio
        assunto_bruto = mensagem.get("Subject")
        assunto = decodificar_texto(assunto_bruto) if assunto_bruto else ""
        
        remetente = mensagem.get("From") or ""

        # Verifica com segurança antes de usar o startswith
        if not assunto or not assunto.startswith("Cadastro Portal Fake -"):
            continue

        nome_cliente = extrair_nome_cliente(remetente)
        _, email_cliente = parseaddr(remetente)

        logging.info(f"Cliente identificado: {nome_cliente} | Assunto: {assunto}")

        encontrou_pdf = False
        arquivos_baixados = []
        caminho_ficha = None
        arquivos_drive = []
        status_documentacao = "Erro"

        for parte in mensagem.walk():
            content_disposition = str(parte.get("Content-Disposition"))
            if "attachment" not in content_disposition: continue

            nome_arquivo = parte.get_filename()
            if not nome_arquivo: continue

            try:
                nome_arquivo = decodificar_texto(nome_arquivo)
            except Exception as e:
                logging.warning(f"Erro ao decodificar nome do arquivo: {e}")
                continue

            if not nome_arquivo.lower().endswith(".pdf"): continue

            try:
                logging.info(f"Fazendo upload do arquivo: {nome_arquivo}")
                conteudo = parte.get_payload(decode=True)
                os.makedirs(PASTA_DOWNLOAD, exist_ok=True)
                caminho_pdf = os.path.join(PASTA_DOWNLOAD, nome_arquivo)

                with open(caminho_pdf, "wb") as arquivo:
                    arquivo.write(conteudo)

                arquivo_id = upload_arquivo(service, caminho_pdf, PASTA_DRIVE_DOWNLOAD)
                arquivos_drive.append({"nome": nome_arquivo, "id": arquivo_id})
                logging.info(f"PDF enviado para o Google Drive: {nome_arquivo}")

            except Exception as e:
                logging.error(f"Erro ao fazer upload do arquivo {nome_arquivo}: {e}")
                continue

            encontrou_pdf = True
            arquivos_baixados.append(nome_arquivo)

            if "ficha_cadastro" in nome_arquivo.lower():
                caminho_ficha = caminho_pdf

        if encontrou_pdf:
            logging.info(f"Documentos encontrados para {nome_cliente}: {', '.join(arquivos_baixados)}")

            if documentacao_completa(arquivos_baixados):
                status_documentacao = "Aprovado"
                logging.info("Documentação COMPLETA.")
                logging.info(f"Enviando confirmação para: {email_cliente}")
                enviar_confirmacao(email_cliente)

                pasta_cliente = criar_subpasta(service, nome_cliente, PASTA_ENCAMINHADOS)
                logging.info(f"Pasta criada para o cliente no Drive.")

                logging.info("Movendo documentos para Documentos_Encaminhados...")
                for arquivo in arquivos_drive:
                    try:
                        mover_arquivo(service, arquivo["id"], pasta_cliente)
                    except Exception as e:
                        logging.error(f"Erro ao mover {arquivo['nome']}: {e}")
            else:
                status_documentacao = "Pendente"
                faltantes = documentos_faltantes(arquivos_baixados)
                logging.warning(f"Documentação INCOMPLETA. Faltantes: {', '.join(faltantes)}")
                
                logging.info(f"Enviando pendência para: {email_cliente}")
                enviar_pendencia(email_cliente, faltantes)

                pasta_cliente = criar_subpasta(service, nome_cliente, PASTA_DOCUMENTOS_PENDENTES)
                logging.info("Movendo documentos para Documentos_Pendentes...")
                for arquivo in arquivos_drive:
                    try:
                        mover_arquivo(service, arquivo["id"], pasta_cliente)
                    except Exception as e:
                        logging.error(f"Erro ao mover {arquivo['nome']}: {e}")

            dados_extraidos_pdf = {} # Dicionário vazio para guardar os dados
            
            if caminho_ficha:
                logging.info("Extraindo dados da ficha cadastral...")
                dados_ficha = extrair_dados_ficha(caminho_ficha)
                if dados_ficha:
                    processar_ficha_cadastral(dados_ficha, status_documentacao)
                    logging.info(f"Planilha atualizada com status: {status_documentacao}")
                    dados_extraidos_pdf = dados_ficha # Guarda os dados aqui!
                else:
                    logging.warning("Não foi possível extrair os dados da ficha.")
                    
            # Agora incluímos os dados reais na lista que vai para o Processo 3
            clientes_processados.append({
                "nome": nome_cliente,
                "email": email_cliente,
                "status_planilha": status_documentacao,
                "cpf": dados_extraidos_pdf.get("CPF", "00000000000"),
                "telefone": dados_extraidos_pdf.get("Telefone", ""),
                "endereco": dados_extraidos_pdf.get("Endereço", ""),
                "nascimento": dados_extraidos_pdf.get("Data de Nascimento", "")
            })
        else:
            logging.warning("Nenhum PDF encontrado neste e-mail.")

    return clientes_processados

def processar_emails():
    try:
        mail = conectar_email()
        resultados = baixar_anexos_pdf(mail)
        mail.logout()
        logging.info("Processo 1 (Leitura de E-mails) finalizado.")
        return resultados
    except Exception as erro:
        logging.error(f"Erro no processamento de e-mails: {erro}")
        return []