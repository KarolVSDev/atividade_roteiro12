
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import gspread
import os
import pickle

from datetime import datetime
from PyPDF2 import PdfReader


# ============================================================
# CONFIGURAÇÕES
# ============================================================

CREDENTIALS_FILE = "client_secret.json"

TOKEN_FILE = "token_sheets.pickle"

URL_PLANILHA = (
    "https://docs.google.com/spreadsheets/d/"
    "1OU_i15E0JluWr-um5zZMZJW1JEbEgNoZtE1jcBXfGzo"
    "/edit?gid=0#gid=0"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# ============================================================
# CONECTAR AO GOOGLE SHEETS
# ============================================================

def conectar_planilha():
    """
    Conecta à planilha do Google Sheets usando OAuth.
    """

    try:

        creds = None

        # ----------------------------------------------------
        # Verifica se já existe um token salvo
        # ----------------------------------------------------

        if os.path.exists(TOKEN_FILE):

            with open(TOKEN_FILE, "rb") as token:

                creds = pickle.load(token)

        # ----------------------------------------------------
        # Verifica se as credenciais são válidas
        # ----------------------------------------------------

        if not creds or not creds.valid:

            # Token expirado, mas pode ser atualizado
            if (
                creds
                and creds.expired
                and creds.refresh_token
            ):

                creds.refresh(Request())

            else:

                # Primeiro acesso: abre o navegador
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE,
                    SCOPES
                )

                creds = flow.run_local_server(
                    port=0
                )

            # ------------------------------------------------
            # Salva o token para os próximos acessos
            # ------------------------------------------------

            with open(TOKEN_FILE, "wb") as token:

                pickle.dump(
                    creds,
                    token
                )

        # ----------------------------------------------------
        # Autoriza o gspread
        # ----------------------------------------------------

        client = gspread.authorize(
            creds
        )

        # ----------------------------------------------------
        # Abre a planilha
        # ----------------------------------------------------

        planilha = client.open_by_url(
            URL_PLANILHA
        )

        print(
            "Conectado ao Google Sheets com sucesso!"
        )

        return planilha

    except Exception as e:

        print(
            f"Erro ao conectar à planilha: {e}"
        )

        return None


# ============================================================
# EXTRAIR DADOS DA FICHA CADASTRAL
# ============================================================

def extrair_dados_ficha(pdf_path):
    """
    Extrai os dados da ficha cadastral a partir do PDF.

    Retorna um dicionário com os dados encontrados.
    """

    try:

        reader = PdfReader(
            pdf_path
        )

        texto = ""

        # ----------------------------------------------------
        # Extrai o texto de todas as páginas
        # ----------------------------------------------------

        for page in reader.pages:

            texto_pagina = page.extract_text()

            if texto_pagina:

                texto += texto_pagina + "\n"

        # ----------------------------------------------------
        # Estrutura dos dados
        # ----------------------------------------------------

        dados = {

            "Nome": "",
            "Sobrenome": "",
            "CPF": "",
            "E-mail": "",
            "Telefone": "",
            "Data de Nascimento": "",
            "Endereço": "",

        }

        # ----------------------------------------------------
        # Percorre as linhas do PDF
        # ----------------------------------------------------

        linhas = texto.split("\n")

        for linha in linhas:

            linha = linha.strip()

            if "Nome:" in linha:

                dados["Nome"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif "Sobrenome:" in linha:

                dados["Sobrenome"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif "CPF:" in linha:

                dados["CPF"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif "E-mail:" in linha:

                dados["E-mail"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif "Telefone:" in linha:

                dados["Telefone"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif "Data de Nascimento:" in linha:

                dados["Data de Nascimento"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

            elif "Endereço:" in linha:

                dados["Endereço"] = (
                    linha.split(
                        ":",
                        1
                    )[1].strip()
                )

        return dados

    except Exception as e:

        print(
            f"Erro ao extrair dados da ficha: {e}"
        )

        return None


# ============================================================
# ATUALIZAR PLANILHA MESTRE
# ============================================================

def atualizar_planilha_mestre(dados):

    try:

        planilha = conectar_planilha()

        if not planilha:
            return

        aba = planilha.sheet1

        nova_linha = [
            # CPF
            dados.get("CPF", ""),

            # Nome
            dados.get("Nome", ""),

            # Data de Nascimento
            dados.get("Data de Nascimento", ""),

            # Endereço
            dados.get("Endereço", ""),

            # E-mail
            dados.get("E-mail", ""),

            # Telefone
            dados.get("Telefone", ""),

            # Status
            dados.get("Status", "Pendente"),

            # Data de Processamento
            datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            ),

            # Observações
            dados.get("Observações", "")
        ]

        aba.append_row(
            nova_linha,
            value_input_option="USER_ENTERED"
        )

        print(
            "Planilha mestre atualizada com sucesso no Google Sheets."
        )

    except Exception as e:

        print(
            f"Erro ao atualizar a planilha mestre: {e}"
        )
# ============================================================
# PROCESSAR FICHA CADASTRAL
# ============================================================

def processar_ficha_cadastral(dados, status):
    """
    Processa os dados da ficha cadastral e atualiza a planilha mestre.
    """
    dados["Status"] = status

    atualizar_planilha_mestre(dados)