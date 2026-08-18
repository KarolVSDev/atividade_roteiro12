import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.processo4.config import EMAIL, SENHA_APP
from src.processo4.logger import logger


def _enviar(destinatario, assunto, corpo):

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
    """
    Comunica ao cliente que o cadastro foi concluído com sucesso.
    Retorna True/False (nunca lança exceção) para permitir fallback
    no fluxo do SAC.
    """

    assunto = "Atendimento concluído - Cadastro aprovado"

    corpo = f"""
Olá, {nome_cliente}!

Seu cadastro (protocolo {protocolo}) foi concluído com sucesso.

Nossa equipe de atendimento confirma o recebimento e o processamento
da sua solicitação.

Atenciosamente,
Equipe SAC - Portal Fake
"""

    try:
        _enviar(email_cliente, assunto, corpo)
        logger.info(
            f"[{protocolo}] E-mail de sucesso enviado para {email_cliente}."
        )
        return True

    except Exception as erro:
        logger.error(
            f"[{protocolo}] Falha ao enviar e-mail de sucesso "
            f"para {email_cliente}: {erro}"
        )
        return False


def notificar_cadastro_com_erro(nome_cliente, email_cliente, protocolo, motivo_erro):
    """
    Comunica ao cliente que houve um problema no cadastro.
    Retorna True/False (nunca lança exceção) para permitir fallback
    no fluxo do SAC.
    """

    assunto = "Atendimento - Pendência no seu cadastro"

    corpo = f"""
Olá, {nome_cliente}!

Identificamos uma pendência no processamento do seu cadastro
(protocolo {protocolo}).

Motivo: {motivo_erro}

Nossa equipe já está ciente e você pode responder este e-mail para
mais informações.

Atenciosamente,
Equipe SAC - Portal Fake
"""

    try:
        _enviar(email_cliente, assunto, corpo)
        logger.info(
            f"[{protocolo}] E-mail de pendência enviado para {email_cliente}."
        )
        return True

    except Exception as erro:
        logger.error(
            f"[{protocolo}] Falha ao enviar e-mail de pendência "
            f"para {email_cliente}: {erro}"
        )
        return False