from playwright.sync_api import sync_playwright
import time
import os

# ===============================================================
# LOGIN NO GCMS / MICROSOFT
# ===============================================================
def realizar_login(page):

    print("Verificando se é necessário fazer login...")

    # ==============================
    # 1 — Tela "Insira a senha"
    # ==============================
    try:
        senha_input = page.get_by_label("Senha", exact=True)
        if senha_input:
            print("Tela de senha detectada. Preenchendo senha...")

            senha_input.fill("Alcoa1234@")

            botao_entrar = page.get_by_role("button", name="Entrar")
            botao_entrar.click()

            page.wait_for_timeout(4000)
    except:
        print("Nenhuma tela de senha encontrada.")

    # ==============================
    # 2 — Tela "Continuar conectado?"
    # ==============================
    try:
        botao_nao = page.get_by_role("button", name="Não")
        if botao_nao:
            print("Tela 'Continuar conectado?' detectada. Clicando NÃO...")
            botao_nao.click()
            page.wait_for_timeout(3000)
    except:
        print("Tela 'Continuar conectado?' não apareceu.")

    print("Login concluído.")


# ===============================================================
# Função: abrir GCMS
# ===============================================================
def abrir_gcms(playwright, base_url):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    page.goto(base_url, timeout=60000)
    print("Página do GCMS carregada.")

    # Executar login automático
    realizar_login(page)

    return browser, context, page


# ===============================================================
# Função: abrir projeto pelo número
# ===============================================================
def abrir_projeto(page, numero_projeto):

    print(f"Abrindo projeto: {numero_projeto}")

    # Abrir menu "+"
    try:
        page.get_by_role("button", name="+").click(timeout=7000)
    except:
        print("[ERRO] Não consegui clicar no botão '+'. Pulando projeto.")
        return False

    # Preencher campo de busca
    try:
        campo = page.get_by_placeholder("Pesquisar por nome ou número...")
        campo.fill(numero_projeto)
    except:
        print("[ERRO] Campo de pesquisa não encontrado.")
        return False

    page.wait_for_timeout(2500)

    resultados = page.locator(f"text={numero_projeto}")

    try:
        count = resultados.count()
    except:
        print("[ERRO] Falha ao ler resultados de busca.")
        return False

    if count == 0:
        print(f"[AVISO] Nenhum resultado encontrado para {numero_projeto}.")
        return False

    # Clicar no primeiro resultado
    try:
        resultados.first.click(timeout=5000)
        print(f"[OK] Projeto {numero_projeto} aberto.")
        return True
    except:
        print(f"[ERRO] Não consegui clicar no projeto {numero_projeto}.")
        return False


# ===============================================================
# Função auxiliar: clique seguro
# ===============================================================
def safe_click(page, description, locator):
    try:
        locator.click(timeout=7000)
        return True
    except:
        print(f"[ERRO] Não consegui clicar em: {description}")
        return False


# ===============================================================
# Baixar Cost Sheet
# ===============================================================
def baixar_cost_sheet(page, numero):

    print("→ Baixando Cost Sheet...")

    try:
        page.get_by_role("treeitem", name="Cost Sheet").click(timeout=6000)
        page.wait_for_timeout(1500)
    except:
        print("[ERRO] Não consegui acessar Cost Sheet.")
        return False

    item = page.locator("text=Project Cost Sheet").first
    if not safe_click(page, "Project Cost Sheet", item):
        return False

    page.wait_for_timeout(2000)

    # Botão de exportação
    try:
        export_btn = page.locator("button").filter(has_text="Print").nth(0)
        export_btn.click(timeout=6000)
    except:
        print("[ERRO] Não consegui abrir menu de exportação.")
        return False

    # Exportar CSV
    try:
        with page.expect_download() as download_info:
            page.locator("text=Export To CSV").click()
        download = download_info.value

        os.makedirs("downloads", exist_ok=True)
        download.save_as(f"downloads/CostSheet_{numero}.csv")

        print(f"[OK] CostSheet salvo: downloads/CostSheet_{numero}.csv")
        return True
    except:
        print("[ERRO] Falha ao exportar CostSheet.")
        return False


# ===============================================================
# Baixar Cash Flow → Actuals
# ===============================================================
def baixar_cashflow_actuals(page, numero):

    print("→ Baixando Cash Flow Actuals...")

    try:
        page.get_by_role("treeitem", name="Cash Flow").click(timeout=6000)
        page.wait_for_timeout(1500)
    except:
        print("[ERRO] Não consegui abrir Cash Flow.")
        return False

    item = page.locator("text=Actuals vs Baseline").first
    if not safe_click(page, "Actuals vs Baseline", item):
        return False

    page.wait_for_timeout(2000)

    # Botão "..."
    try:
        tres = page.locator("button").filter(has_text="...").nth(0)
        tres.click(timeout=6000)
    except:
        print("[ERRO] Não consegui abrir menu de curvas.")
        return False

    # Selecionar curva Actuals
    try:
        page.locator("text=Actual").first.click(timeout=5000)
    except:
        print("[ERRO] Curva 'Actual' não encontrada.")
        return False

    # Exportar CSV
    try:
        with page.expect_download() as download_info:
            page.locator("text=Export").first.click()
        download = download_info.value

        os.makedirs("downloads", exist_ok=True)
        download.save_as(f"downloads/CashFlow_Actuals_{numero}.csv")

        print(f"[OK] Actuals salvo: downloads/CashFlow_Actuals_{numero}.csv")
        return True
    except:
        print("[ERRO] Falha ao exportar Actuals.")
        return False


# ===============================================================
# Baixar Cash Flow → Forecast
# ===============================================================
def baixar_cashflow_forecast(page, numero):

    print("→ Baixando Cash Flow Forecast...")

    try:
        page.get_by_role("treeitem", name="Cash Flow").click(timeout=6000)
        page.wait_for_timeout(1500)
    except:
        print("[ERRO] Não consegui abrir Cash Flow.")
        return False

    item = page.locator("text=Cash Flow by CBS").first
    if not safe_click(page, "Cash Flow by CBS", item):
        return False

    page.wait_for_timeout(2000)

    # Botão "..."
    try:
        tres = page.locator("button").filter(has_text="...").nth(0)
        tres.click(timeout=6000)
    except:
        print("[ERRO] Não consegui abrir menu de curvas.")
        return False

    # Selecionar Forecast
    try:
        page.locator("text=Forecast").first.click(timeout=5000)
    except:
        print("[ERRO] Curva Forecast não encontrada.")
        return False

    # Exportar CSV
    try:
        with page.expect_download() as download_info:
            page.locator("text=Export").first.click()
        download = download_info.value

        os.makedirs("downloads", exist_ok=True)
        download.save_as(f"downloads/CashFlow_Forecast_{numero}.csv")

        print(f"[OK] Forecast salvo: downloads/CashFlow_Forecast_{numero}.csv")
        return True
    except:
        print("[ERRO] Falha ao exportar Forecast.")
        return False


# ===============================================================
# Função principal por projeto
# ===============================================================
def executar_fluxo(numero_projeto, base_url):

    print("\n==============================================")
    print(f"EXECUTANDO PROJETO: {numero_projeto}")
    print("==============================================\n")

    try:
        with sync_playwright() as pw:
            browser, context, page = abrir_gcms(pw, base_url)

            # Tentar abrir projeto
            if not abrir_projeto(page, numero_projeto):
                print(f"[AVISO] Projeto {numero_projeto} ignorado.")
                context.close()
                browser.close()
                return False

            baixar_cost_sheet(page, numero_projeto)
            baixar_cashflow_actuals(page, numero_projeto)
            baixar_cashflow_forecast(page, numero_projeto)

            context.close()
            browser.close()
            return True

    except Exception as e:
        print(f"[ERRO] Erro crítico no projeto {numero_projeto}: {e}")
        return False
