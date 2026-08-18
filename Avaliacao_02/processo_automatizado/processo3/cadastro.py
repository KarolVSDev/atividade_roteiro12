import logging
import time
import base64
from pathlib import Path
from datetime import datetime
import os
from botcity.web import WebBot, Browser, By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Caminho dinâmico para o Portal Fake (funciona no Windows, Linux e Docker)
PORTAL_HTML = Path(__file__).resolve().parents[1] / "portal_fake" / "index.html"
DELAY = 0.5

def iniciar_bot():
    bot = WebBot()
    bot.headless = True 
    bot.browser = Browser.CHROME
    bot.driver_path = ChromeDriverManager().install()
    
    # Configura as opções do Chrome corretamente para o ambiente Docker (Linux)
    if os.path.exists("/.dockerenv"):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Se você precisar passar as opções para o driver subjacente do BotCity:
        # bot.options = options # (caso sua versão aceite)
    
    bot.start_browser()
    return bot

def abrir_portal(bot):
    # Converte o path para a URL local aceita pelo navegador
    url = "file:///" + str(PORTAL_HTML).replace("\\", "/")
    bot.browse(url)
    WebDriverWait(bot.driver, timeout=10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "#btnNovo"))
    )

def fallback_cadastro(cliente, erro):
    """Plano B caso o Selenium/Portal falhe."""
    logging.warning(f"Fallback acionado para {cliente.get('nome')}. Motivo: {erro}")
    cliente['status_cadastro'] = 'Erro de Automação (Salvo em contingência)'
    cliente['detalhe_erro'] = str(erro)
    return cliente

def b_cadastrar_usuario(bot, cliente):
    bot.find_element("#btnNovo", By.CSS_SELECTOR).click()
    time.sleep(DELAY)

    # Tratamento do nome (dividindo em nome e sobrenome, pois o portal exige os 2)
    nome_completo = cliente.get('nome', 'Cliente').split()
    primeiro_nome = nome_completo[0]
    sobrenome = " ".join(nome_completo[1:]) if len(nome_completo) > 1 else "Não Informado"

    # Mapeia o status da planilha para o select do portal
    status_map = {
        "Aprovado": "ATIVO",
        "Pendente": "PENDENTE",
        "Erro": "BLOQUEADO"
    }
    status_portal = status_map.get(cliente.get('status_planilha'), "PENDENTE")

    # Mapeamento dinâmico dos campos usando os dados que vieram do Processo 1
    campos = [
        ("f_nome", primeiro_nome),
        ("f_sobrenome", sobrenome),
        ("f_cpf", cliente.get("cpf", "00000000000")),
        ("f_telefone", cliente.get("telefone", "")),
        ("f_email", cliente.get("email", "email@exemplo.com")),
        ("f_endereco", cliente.get("endereco", "Cadastrado Automaticamente via RPA")),
        ("f_observacao", f"Status Planilha: {cliente.get('status_planilha')}")
    ]

    for campo_id, valor in campos:
        el = bot.find_element(f"#{campo_id}", By.CSS_SELECTOR)
        el.clear()
        el.send_keys(str(valor))

    Select(bot.find_element("#f_status", By.CSS_SELECTOR)).select_by_value(status_portal)
    bot.find_element('#btnSalvar', By.CSS_SELECTOR).click()
    time.sleep(DELAY)

def tirar_screenshot(bot, arquivo=None):
    try:
        # Se nenhum nome específico for passado, gera um nome único com data e hora atual
        if not arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"evidencia_cadastro_{timestamp}.png"
            
        # Define o caminho para a pasta 'evidencias' na raiz do projeto
        pasta_evidencias = Path(__file__).resolve().parents[1] / "evidencias"
        
        # Cria a pasta automaticamente se ela não existir
        pasta_evidencias.mkdir(exist_ok=True)
        
        # Monta o caminho completo onde a imagem será salva
        caminho_completo = pasta_evidencias / arquivo

        # Tira o print via protocolo CDP do Chrome
        result = bot.driver.execute_cdp_cmd("Page.captureScreenshot", {
            "format": "png",
            "captureBeyondViewport": True
        })
        
        # Salva o arquivo no caminho novo
        with open(caminho_completo, "wb") as f:
            f.write(base64.b64decode(result['data']))
            
        logging.info(f"Screenshot salvo em: {caminho_completo}")
        
    except Exception as e:
        logging.error(f"Erro ao tirar screenshot: {e}")

def executar_cadastro(dados_clientes):
    logging.info("--- Iniciando Processo 3: Cadastro no Portal Fake ---")
    
    if not dados_clientes:
        logging.warning("Nenhum dado recebido para cadastro.")
        return []

    resultados_cadastro = []
    bot = None
    
    try:
        logging.info("Iniciando navegador (WebBot)...")
        bot = iniciar_bot()
        abrir_portal(bot)

        total = len(dados_clientes)
        for i, cliente in enumerate(dados_clientes, start=1):
            logging.info(f"Cadastrando [{i}/{total}]: {cliente.get('nome')}")
            
            try:
                # Tenta realizar o cadastro via interface Web
                b_cadastrar_usuario(bot, cliente)
                cliente['status_cadastro'] = 'Sucesso'
                logging.info(f"Cadastro Web realizado com sucesso: {cliente.get('nome')}")
                resultados_cadastro.append(cliente)
                
            except Exception as e:
                logging.error(f"Falha ao manipular formulário para {cliente.get('nome')}: {e}")
                cliente_com_erro = fallback_cadastro(cliente, e)
                resultados_cadastro.append(cliente_com_erro)

        tirar_screenshot(bot)
        
    except Exception as general_error:
        logging.error(f"Erro crítico ao abrir o navegador/portal: {general_error}")
        # Se o portal não abrir de jeito nenhum, aciona fallback pra todos os clientes
        for cliente in dados_clientes:
            resultados_cadastro.append(fallback_cadastro(cliente, general_error))
    finally:
        if bot:
            logging.info("Fechando navegador do Processo 3.")
            bot.stop_browser()

    logging.info(f"Processo 3 concluído. Total processado: {len(resultados_cadastro)}")
    return resultados_cadastro