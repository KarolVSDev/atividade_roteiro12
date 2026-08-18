from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import logging
from datetime import datetime
from PyPDF2 import PdfReader

try:
    import gspread
except ImportError:
    gspread = None

CREDENTIALS_FILE = "client_secret.json"
TOKEN_FILE = "token_sheets.pickle"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1OU_i15E0JluWr-um5zZMZJW1JEbEgNoZtE1jcBXfGzo/edit?gid=0#gid=0"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

if gspread is None:
    raise ImportError("A biblioteca 'gspread' é obrigatória. Instale com: pip install gspread")

def conectar_planilha():
    try:
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)

        client = gspread.authorize(creds)
        planilha = client.open_by_url(URL_PLANILHA)
        logging.info("Conectado ao Google Sheets com sucesso!")
        return planilha
    except Exception as e:
        logging.error(f"Erro ao conectar à planilha: {e}")
        return None

def extrair_dados_ficha(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        texto = ""
        for page in reader.pages:
            texto_pagina = page.extract_text()
            if texto_pagina:
                texto += texto_pagina + "\n"

        dados = {
            "Nome": "", "Sobrenome": "", "CPF": "", "E-mail": "",
            "Telefone": "", "Data de Nascimento": "", "Endereço": "",
        }

        linhas = texto.split("\n")
        for linha in linhas:
            linha = linha.strip()
            if "Nome:" in linha: dados["Nome"] = linha.split(":", 1)[1].strip()
            elif "Sobrenome:" in linha: dados["Sobrenome"] = linha.split(":", 1)[1].strip()
            elif "CPF:" in linha: dados["CPF"] = linha.split(":", 1)[1].strip()
            elif "E-mail:" in linha: dados["E-mail"] = linha.split(":", 1)[1].strip()
            elif "Telefone:" in linha: dados["Telefone"] = linha.split(":", 1)[1].strip()
            elif "Data de Nascimento:" in linha: dados["Data de Nascimento"] = linha.split(":", 1)[1].strip()
            elif "Endereço:" in linha: dados["Endereço"] = linha.split(":", 1)[1].strip()

        return dados
    except Exception as e:
        logging.error(f"Erro ao extrair dados da ficha: {e}")
        return None

def atualizar_planilha_mestre(dados):
    try:
        planilha = conectar_planilha()
        if not planilha: return

        aba = planilha.sheet1
        nova_linha = [
            dados.get("CPF", ""),
            dados.get("Nome", ""),
            dados.get("Data de Nascimento", ""),
            dados.get("Endereço", ""),
            dados.get("E-mail", ""),
            dados.get("Telefone", ""),
            dados.get("Status", "Pendente"),
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            dados.get("Observações", "")
        ]

        aba.append_row(nova_linha, value_input_option="USER_ENTERED")
        logging.info("Planilha mestre atualizada com sucesso no Google Sheets.")
    except Exception as e:
        logging.error(f"Erro ao atualizar a planilha mestre: {e}")

def processar_ficha_cadastral(dados, status):
    dados["Status"] = status
    atualizar_planilha_mestre(dados)