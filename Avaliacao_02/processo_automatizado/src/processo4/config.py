import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# CAMINHOS
# ============================================================

# Raiz do processo_automatizado (.env fica lá, junto do Processo 1/2)
APP_ROOT = Path(__file__).resolve().parents[2]

PROCESSO4_ROOT = Path(__file__).resolve().parent

# Pasta de contrato com o Processo 3: é aqui que o resultado do
# cadastro (um arquivo .json por solicitação) deve ser depositado.
PASTA_ENTRADA_PROCESSO3 = PROCESSO4_ROOT / "entrada_processo3"

# Pasta de contrato com o Processo 5: aqui o SAC deposita o
# resultado do atendimento para o próximo setor.
PASTA_SAIDA_PROCESSO5 = PROCESSO4_ROOT / "saida_processo5"

# Arquivos de entrada já tratados são arquivados aqui
# (evita reprocessar o mesmo arquivo em duas execuções).
PASTA_PROCESSADO = PROCESSO4_ROOT / "processado"

# Entradas que falharam na validação/​processamento e precisam
# de conferência manual (fallback).
PASTA_ERRO = PROCESSO4_ROOT / "erro_processamento"

PASTA_LOGS = PROCESSO4_ROOT / "logs"

ARQUIVO_LOG_TEXTO = PASTA_LOGS / "processo4.log"
ARQUIVO_LOG_ATENDIMENTOS = PASTA_LOGS / "atendimentos.csv"

for pasta in (
    PASTA_ENTRADA_PROCESSO3,
    PASTA_SAIDA_PROCESSO5,
    PASTA_PROCESSADO,
    PASTA_ERRO,
    PASTA_LOGS,
):
    pasta.mkdir(parents=True, exist_ok=True)


# ============================================================
# CREDENCIAIS DE E-MAIL (reaproveita o .env do Processo 1/2)
# ============================================================

ENV_PATH = APP_ROOT / ".env"
load_dotenv(ENV_PATH)

EMAIL = os.getenv("EMAIL") or os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP") or os.getenv("EMAIL_SENHA")
