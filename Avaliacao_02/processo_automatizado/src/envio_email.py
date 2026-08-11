import os
import smtplib

from dotenv import load_dotenv
from pathlib import Path

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Carrega o .env da pasta app do projeto
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

EMAIL = os.getenv("EMAIL") or os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP") or os.getenv("EMAIL_SENHA")


def enviar_confirmacao(destinatario):

    assunto = "Confirmação de Recebimento de Documentação"

    corpo = f"""
Olá,

Recebemos sua documentação com sucesso.

Os documentos enviados foram analisados e encaminhados para processamento.

Documentos recebidos:
- RG
- CPF
- Comprovante de Residência

Atenciosamente,

Equipe Portal Fake
"""

    try:

        mensagem = MIMEMultipart()

        mensagem["From"] = EMAIL
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto

        mensagem.attach(
            MIMEText(
                corpo,
                "plain",
                "utf-8"
            )
        )

        servidor = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        servidor.starttls()

        servidor.login(
            EMAIL,
            SENHA_APP
        )

        servidor.send_message(
            mensagem
        )

        servidor.quit()

        print(
            f"E-mail enviado com sucesso para {destinatario}"
        )

        return True

    except Exception as erro:

        print(
            f"Erro ao enviar e-mail: {erro}"
        )

        return False


def enviar_pendencia(
    destinatario,
    documentos_faltantes
):

    assunto = "Pendência na Documentação"

    lista_documentos = "\n".join(
        f"- {doc}"
        for doc in documentos_faltantes
    )

    corpo = f"""
Olá,

Recebemos sua documentação, porém ela está incompleta.

Documentos faltantes:

{lista_documentos}

Por favor, envie os documentos pendentes para continuidade do atendimento.

Atenciosamente,

Equipe Portal Fake
"""

    try:

        mensagem = MIMEMultipart()

        mensagem["From"] = EMAIL
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto

        mensagem.attach(
            MIMEText(
                corpo,
                "plain",
                "utf-8"
            )
        )

        servidor = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        servidor.starttls()

        servidor.login(
            EMAIL,
            SENHA_APP
        )

        servidor.send_message(
            mensagem
        )

        servidor.quit()

        print(
            f"E-mail de pendência enviado para {destinatario}"
        )

        return True

    except Exception as erro:

        print(
            f"Erro ao enviar e-mail: {erro}"
        )

        return False


if __name__ == "__main__":

    # Teste
    enviar_confirmacao(
        "seu_email_teste@gmail.com"
    )