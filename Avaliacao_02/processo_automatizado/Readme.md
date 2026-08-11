# Automação de Atendimento — Portal Fake

##  Descrição

Este projeto consiste em uma automação desenvolvida em Python para realizar o processamento automático de solicitações recebidas por e-mail.

O robô monitora a caixa de entrada do Gmail, identifica e-mails relacionados a cadastros, baixa os documentos PDF anexados, verifica se a documentação necessária foi enviada, registra os dados em uma planilha do Google Sheets e organiza os documentos no Google Drive.

---

## Objetivo da Automação

O principal objetivo é **automatizar o processo de recebimento, validação e organização de documentos cadastrais**, reduzindo atividades manuais e tornando o fluxo de atendimento mais rápido e organizado.

A automação realiza as seguintes etapas:

1. Conecta-se à conta de e-mail.
2. Identifica e-mails não lidos relacionados ao cadastro.
3. Identifica o cliente pelo remetente.
4. Baixa os arquivos PDF anexados.
5. Envia os documentos para uma pasta no Google Drive.
6. Verifica se a documentação está completa.
7. Extrai os dados da ficha cadastral.
8. Registra os dados no Google Sheets.
9. Define o status do cadastro:

   * **Aprovado** — quando toda a documentação obrigatória foi enviada.
   * **Pendente** — quando existe algum documento obrigatório faltando.
10. Registra automaticamente a data de processamento.
11. Envia um e-mail de confirmação ou pendência ao cliente.
12. Organiza os documentos no Google Drive em uma subpasta com o nome do cliente.

---

## Tecnologias Utilizadas

### Linguagem

* **Python 3**

### Bibliotecas

* `imaplib` — conexão e leitura de e-mails via IMAP.
* `email` — processamento das mensagens e anexos.
* `python-dotenv` — carregamento de variáveis de ambiente.
* `google-api-python-client` — integração com Google Drive.
* `gspread` — integração com Google Sheets.
* `google-auth` — autenticação nas APIs do Google.
* `google-auth-oauthlib` — autenticação OAuth 2.0.
* `PyPDF2` — extração de texto dos arquivos PDF.
* `pickle` — armazenamento local dos tokens de autenticação.

### Serviços utilizados

* **Gmail** — recebimento e processamento dos e-mails.
* **Google Drive** — armazenamento e organização dos documentos.
* **Google Sheets** — registro dos dados cadastrais.

---

## Estrutura do Projeto

```text
processo_automatizado/
│
├── src/
│   ├── bot.py
│   ├── email_monitor.py
│   ├── drive.py
│   ├── envio_email.py
│   ├── preencher_planilha.py
│   │
│   └── downloads/
│
├── .env
├── client_secret.json
├── token.pickle
├── token_sheets.pickle
├── requirements.txt
└── README.md
```

### Principais arquivos

**`bot.py`**

Arquivo responsável por iniciar a execução da automação.

**`email_monitor.py`**

Responsável por:

* Conectar ao Gmail;
* Buscar e-mails não lidos;
* Identificar e-mails de cadastro;
* Processar os anexos;
* Verificar a documentação;
* Acionar as demais etapas da automação.

**`drive.py`**

Responsável pela integração com o Google Drive, incluindo:

* Autenticação;
* Upload dos documentos;
* Criação de subpastas;
* Movimentação dos arquivos.

**`preencher_planilha.py`**

Responsável por:

* Extrair informações da ficha cadastral em PDF;
* Conectar ao Google Sheets;
* Inserir os dados na planilha;
* Registrar o status da documentação;
* Registrar a data de processamento.

**`envio_email.py`**

Responsável pelo envio dos e-mails de confirmação e de pendência.

---

## Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

* Python 3
* Git
* Uma conta Google
* Acesso ao Gmail
* Acesso às APIs do Google Drive e Google Sheets

Recomenda-se utilizar um ambiente virtual Python.

---

## Instalação

### 1. Clone o repositório

```bash
git clone URL_DO_REPOSITORIO
```

Entre na pasta do projeto:

```bash
cd processo_automatizado
```

### 2. Crie o ambiente virtual

No Windows:

```bash
python -m venv av2
```

Ative o ambiente:

```bash
av2\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

Caso o arquivo `requirements.txt` ainda não exista, instale as principais dependências:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib gspread python-dotenv PyPDF2
```

---

## Configuração das credenciais

### Gmail

Configure as informações da conta de e-mail no arquivo `.env`:

```env
EMAIL=seu_email@gmail.com
SENHA_APP=sua_senha_de_aplicativo
```

A senha utilizada deve ser uma **Senha de App do Google**, quando a autenticação da conta exigir esse método.

### Google APIs

É necessário configurar as credenciais OAuth do Google Cloud e colocar o arquivo:

```text
client_secret.json
```

na pasta principal do projeto.

Na primeira execução, o sistema poderá solicitar autorização para acessar o Google Drive e o Google Sheets.

Após a autenticação, os tokens são armazenados localmente para evitar a necessidade de autenticação em todas as execuções.

> **Importante:** arquivos como `.env`, `client_secret.json`, `token.pickle` e `token_sheets.pickle` não devem ser enviados para repositórios públicos.

---

## Google Sheets

A planilha utilizada pela automação deve estar configurada para receber os dados cadastrais.

Os principais campos utilizados são:

| Campo                 | Descrição               |
| --------------------- | ----------------------- |
| CPF                   | CPF do cliente          |
| Nome                  | Nome do cliente         |
| Data de Nascimento    | Data de nascimento      |
| Endereço              | Endereço informado      |
| E-mail                | E-mail do cliente       |
| Telefone              | Telefone informado      |
| Status                | Aprovado ou Pendente    |
| Data de Processamento | Data e hora da execução |
| Observações           | Informações adicionais  |

---

## Organização dos documentos

Os documentos recebidos são inicialmente enviados para uma pasta de processamento no Google Drive.

Após a análise da documentação:

### Documentação completa

Os arquivos são organizados na pasta:

```text
Documentos_Encaminhados/
└── Nome do Cliente/
    ├── CPF.pdf
    ├── RG.pdf
    ├── COMPROVANTE DE RESIDENCIA.pdf
    └── Ficha_Cadastro_Portal_Fake.pdf
```

O cadastro recebe o status:

```text
Aprovado
```

### Documentação incompleta

Quando algum documento obrigatório não é encontrado, o cadastro recebe o status:

```text
Pendente
```

Os documentos são organizados na pasta de documentos pendentes, em uma subpasta com o nome do cliente.

Além disso, o cliente recebe um e-mail informando quais documentos estão faltando.

---

## Documentos obrigatórios

Atualmente, a automação verifica a existência dos seguintes documentos:

* CPF
* RG
* Comprovante de residência

A presença desses documentos determina se o cadastro será considerado **Aprovado** ou **Pendente**.

---

## Execução

Com o ambiente virtual ativado, execute:

```bash
python src/bot.py
```

Ou, caso esteja dentro da pasta `src`:

```bash
python bot.py
```

Durante a execução, o terminal exibirá informações como:

```text
Iniciando robô de atendimento...

Conectando ao Gmail...
Login realizado com sucesso!

E-mail(s) encontrados.

Cliente identificado: Nome do Cliente

Fazendo upload do arquivo: CPF.pdf
PDF enviado para o Google Drive: CPF.pdf

Documentação COMPLETA.

Enviando confirmação para: cliente@email.com

Planilha atualizada com status: Aprovado

Processo finalizado.
```

---

## Fluxo da Automação

```text
Gmail
  │
  ▼
Identificação do e-mail
  │
  ▼
Download dos PDFs
  │
  ▼
Upload para o Google Drive
  │
  ▼
Verificação da documentação
  │
  ├── Completa ──────► Aprovado
  │                       │
  │                       ├── Atualiza Google Sheets
  │                       ├── Envia confirmação
  │                       └── Organiza documentos
  │
  └── Incompleta ────► Pendente
                          │
                          ├── Atualiza Google Sheets
                          ├── Envia e-mail de pendência
                          └── Organiza documentos
```

---

## Segurança

Não versionar informações sensíveis ou credenciais.

Recomenda-se adicionar ao `.gitignore`:

```gitignore
.env
client_secret.json
token.pickle
token_sheets.pickle
__pycache__/
*.pyc
downloads/
```

---

## Projeto

Projeto desenvolvido como parte das atividades de **Hyperautomação**, utilizando Python e integração com serviços do Google para automatização do processo de atendimento e processamento de documentos.
