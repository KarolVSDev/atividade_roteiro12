import imaplib
import email as email_module
from email.header import decode_header
import os
import socket
from email.utils import parseaddr
from email.utils import parseaddr
from pathlib import Path
import sys
from src.preencher_planilha import processar_ficha_cadastral, extrair_dados_ficha

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.envio_email import (
    enviar_confirmacao,
    enviar_pendencia
)

from dotenv import load_dotenv

from src.drive import (
    autenticar_google_drive,
    upload_arquivo,
    criar_subpasta,
    mover_arquivo,
    PASTA_ENCAMINHADOS,
    PASTA_DOCUMENTOS_OK,
    PASTA_DRIVE_DOWNLOAD,
    PASTA_DOWNLOAD,
    PASTA_DOCUMENTOS_PENDENTES
)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

EMAIL = os.getenv("EMAIL") or os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP") or os.getenv("EMAIL_SENHA")

print("EMAIL carregado:", EMAIL)
print(
    "SENHA_APP carregada:",
    SENHA_APP is not None
)

PASTA_DRIVE_DOWNLOAD = "1dMZwGTF3X_45AgDZ2yd3dWO5TTlWhu3-"


def conectar_email():

    print("\nTestando DNS...")

    ip = socket.gethostbyname(
        "imap.gmail.com"
    )

    print(
        f"imap.gmail.com -> {ip}"
    )

    print("Conectando ao Gmail...")

    mail = imaplib.IMAP4_SSL(
        "imap.gmail.com",
        993
    )

    print("Realizando login...")

    mail.login(
        EMAIL,
        SENHA_APP
    )

    print(
        "Login realizado com sucesso!"
    )

    return mail

def extrair_nome_cliente(remetente):

    nome, email = parseaddr(remetente)

    if nome:
        return nome.strip()

    return email.split("@")[0]



    # remetente = mensagem.get("From")
    # nome_cliente = extrair_nome_cliente(remetente)

    # print(
    #     f"Cliente identificado: {nome_cliente}"
    # )

def decodificar_texto(texto):
    if texto is None:
        return ""

    partes = decode_header(texto)
    resultado = ""

    for valor, encoding in partes:
        if isinstance(valor, bytes):
            try:
                resultado += valor.decode(
                    encoding or "utf-8",
                    errors="replace"
                )
            except (UnicodeDecodeError, LookupError):
                resultado += valor.decode(
                    "latin-1",
                    errors="replace"
                )
        else:
            resultado += valor

    return resultado

def documentacao_completa(
    lista_arquivos
):

    encontrou_rg = False
    encontrou_cpf = False
    encontrou_comprovante = False

    for arquivo in lista_arquivos:

        nome = arquivo.lower()

        if "rg" in nome:
            encontrou_rg = True

        if "cpf" in nome:
            encontrou_cpf = True

        if "comprovante" in nome:
            encontrou_comprovante = True

    return (
        encontrou_rg
        and encontrou_cpf
        and encontrou_comprovante
    )

def documentos_faltantes(lista_arquivos):

    documentos = {
        "RG": False,
        "CPF": False,
        "COMPROVANTE DE RESIDENCIA": False
    }


    for arquivo in lista_arquivos:

        nome = arquivo.upper()


        if "RG" in nome:
            documentos["RG"] = True


        if "CPF" in nome:
            documentos["CPF"] = True


        if (
            "COMPROVANTE" in nome
            or "RESIDENCIA" in nome
        ):
            documentos["COMPROVANTE DE RESIDENCIA"] = True



    faltantes = []


    for documento, encontrado in documentos.items():

        if not encontrado:
            faltantes.append(documento)


    return faltantes

from src.drive import (
    criar_subpasta,
    upload_arquivo,
    PASTA_ENCAMINHADOS,
    PASTA_DOCUMENTOS_PENDENTES
)

# ...código existente...

def baixar_anexos_pdf(mail):

    LIMITE_EMAILS = 10

    mail.select("INBOX")

    status, mensagens = mail.search(
        None,
        "UNSEEN"
    )

    if status != "OK":
        print(
            "Erro ao buscar mensagens."
        )
        return

    ids_emails = mensagens[0].split()

    ids_emails = ids_emails[-LIMITE_EMAILS:]
    ids_emails.reverse()

    if not ids_emails:

        print(
            "Nenhum e-mail não lido encontrado."
        )
        return

    print(
        f"\n{len(ids_emails)} e-mail(s) encontrados.\n"
    )

    service = autenticar_google_drive()

    for email_id in ids_emails:

        status, dados = mail.fetch(
            email_id,
            "(RFC822)"
        )

        if status != "OK":
            continue

        mensagem = email_module.message_from_bytes(
            dados[0][1]
        )

        assunto = decodificar_texto(
            mensagem.get("Subject")
        )

        remetente = mensagem.get("From")

        if not assunto.startswith(
            "Cadastro Portal Fake -"
        ):
            continue

        nome_cliente = extrair_nome_cliente(
            remetente
        )

        print(
            f"Cliente identificado: {nome_cliente}"
        )

        print(
            "\n" + "=" * 50
        )

        print(
            f"Assunto: {assunto}"
        )

        print(
            f"Remetente: {remetente}"
        )

        encontrou_pdf = False

        arquivos_baixados = []

        caminho_ficha = None

        # Guarda ID e nome dos arquivos no Drive
        arquivos_drive = []

        # ==========================================
        # PROCESSAR ANEXOS
        # ==========================================

        for parte in mensagem.walk():

            content_disposition = str(
                parte.get(
                    "Content-Disposition"
                )
            )

            if "attachment" not in content_disposition:
                continue

            nome_arquivo = parte.get_filename()

            if not nome_arquivo:
                continue

            try:

                nome_arquivo = decodificar_texto(
                    nome_arquivo
                )

            except Exception as e:

                print(
                    f"Erro ao decodificar o nome "
                    f"do arquivo: {e}"
                )

                continue

            if not nome_arquivo.lower().endswith(".pdf"):
                continue

            try:

                print(
                    f"Fazendo upload do arquivo: "
                    f"{nome_arquivo}"
                )

                conteudo = parte.get_payload(
                    decode=True
                )

                os.makedirs(
                    PASTA_DOWNLOAD,
                    exist_ok=True
                )

                caminho_pdf = os.path.join(
                    PASTA_DOWNLOAD,
                    nome_arquivo
                )

                # Salvar PDF localmente
                with open(
                    caminho_pdf,
                    "wb"
                ) as arquivo:

                    arquivo.write(conteudo)

                # ==================================
                # UPLOAD PARA O GOOGLE DRIVE
                # ==================================

                arquivo_id = upload_arquivo(
                    service,
                    caminho_pdf,
                    PASTA_DRIVE_DOWNLOAD
                )

                # Guardar nome + ID
                arquivos_drive.append(
                    {
                        "nome": nome_arquivo,
                        "id": arquivo_id
                    }
                )

                print(
                    f"PDF enviado para o Google Drive: "
                    f"{nome_arquivo}"
                )

            except Exception as e:

                print(
                    f"Erro ao fazer upload do arquivo "
                    f"{nome_arquivo}: {e}"
                )

                continue

            encontrou_pdf = True

            arquivos_baixados.append(
                nome_arquivo
            )

            # ==================================
            # IDENTIFICAR FICHA CADASTRAL
            # ==================================

            if "ficha_cadastro" in nome_arquivo.lower():

                caminho_ficha = caminho_pdf

        # ==========================================
        # VERIFICAR SE ENCONTROU PDF
        # ==========================================

        if encontrou_pdf:

            print(
                "\nDocumentos encontrados:"
            )

            for arquivo in arquivos_baixados:

                print(
                    f" - {arquivo}"
                )

            # ======================================
            # VERIFICAR DOCUMENTAÇÃO
            # ======================================

            if documentacao_completa(
                arquivos_baixados
            ):

                status_documentacao = "Aprovado"

                print(
                    "\nDocumentação COMPLETA."
                )

                nome, email_cliente = parseaddr(
                    remetente
                )

                print(
                    f"Enviando confirmação para: "
                    f"{email_cliente}"
                )

                enviar_confirmacao(
                    email_cliente
                )

                # ==================================
                # CRIAR PASTA DO CLIENTE
                # ==================================

                pasta_cliente = criar_subpasta(
                    service,
                    nome_cliente,
                    PASTA_ENCAMINHADOS
                )

                print(
                    f"\nPasta criada para o cliente: "
                    f"{nome_cliente}"
                )

                # ==================================
                # MOVER DOCUMENTOS
                # ==================================

                print(
                    "\nMovendo documentos para "
                    "Documentos_Encaminhados..."
                )

                for arquivo in arquivos_drive:

                    try:

                        mover_arquivo(
                            service,
                            arquivo["id"],
                            pasta_cliente
                        )

                    except Exception as e:

                        print(
                            f"Erro ao mover "
                            f"{arquivo['nome']}: {e}"
                        )

            # ======================================
            # DOCUMENTAÇÃO INCOMPLETA
            # ======================================

            else:

                status_documentacao = "Pendente"

                print(
                    "\nDocumentação INCOMPLETA."
                )

                nome, email_cliente = parseaddr(
                    remetente
                )

                faltantes = documentos_faltantes(
                    arquivos_baixados
                )

                print(
                    "\nDocumentos faltantes:"
                )

                for doc in faltantes:

                    print(
                        f"- {doc}"
                    )

                print(
                    f"\nEnviando pendência para: "
                    f"{email_cliente}"
                )

                enviar_pendencia(
                    email_cliente,
                    faltantes
                )

                # ==================================
                # CRIAR PASTA DE PENDÊNCIAS
                # ==================================

                pasta_cliente = criar_subpasta(
                    service,
                    nome_cliente,
                    PASTA_DOCUMENTOS_PENDENTES
                )

                print(
                    f"\nPasta de pendências criada "
                    f"para: {nome_cliente}"
                )

                # ==================================
                # MOVER DOCUMENTOS PARA PENDENTES
                # ==================================

                print(
                    "\nMovendo documentos para "
                    "Documentos_Pendentes..."
                )

                for arquivo in arquivos_drive:

                    try:

                        mover_arquivo(
                            service,
                            arquivo["id"],
                            pasta_cliente
                        )

                    except Exception as e:

                        print(
                            f"Erro ao mover "
                            f"{arquivo['nome']}: {e}"
                        )

            # ======================================
            # ATUALIZAR PLANILHA
            # ======================================

            if caminho_ficha:

                print(
                    "\nExtraindo dados da "
                    "ficha cadastral..."
                )

                dados_ficha = extrair_dados_ficha(
                    caminho_ficha
                )

                if dados_ficha:

                    processar_ficha_cadastral(
                        dados_ficha,
                        status_documentacao
                    )

                    print(
                        f"Planilha atualizada com status: "
                        f"{status_documentacao}"
                    )

                else:

                    print(
                        "Não foi possível extrair "
                        "os dados da ficha."
                    )

        else:

            print(
                "\nNenhum PDF encontrado."
            )

        print(
            "=" * 50
        )
def processar_emails():

    try:

        mail = conectar_email()

        baixar_anexos_pdf(
            mail
        )

        mail.logout()

        print(
            "\nProcesso finalizado."
        )

    except Exception as erro:

        print(
            f"\nErro: {erro}"
        )


def main():
    processar_emails()


if __name__ == "__main__":
    main()