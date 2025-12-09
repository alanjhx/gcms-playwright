from playwright.sync_api import sync_playwright
import time

def gcms_login(usuario: str, senha: str):
    """
    Abre o GCMS, faz login e retorna o objeto 'page' já autenticado.
    """

    with sync_playwright() as p:
        # abre navegador invisível (headless)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("Acessando GCMS...")

        # COLOQUE AQUI A URL REAL DO GCMS:
        page.goto("https://unifier.oraclecloud.com/alcoa/bp/g/nav/index?__uref=uuu983602594")  
        page.wait_for_load_state("networkidle")

        # Aguarda os campos aparecerem
        print("Preenchendo usuário...")
        page.fill("input[id='username']", usuario)
        
        print("Preenchendo senha...")
        page.fill("input[id='password']", senha)

        print("Clicando em Login...")
        page.click("button[type='submit'], input[type='submit'], #loginBtn")

        # Espera carregar completamente
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        print("Login realizado.")
        return page, browser
