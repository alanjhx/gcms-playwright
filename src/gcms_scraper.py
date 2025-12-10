from playwright.sync_api import sync_playwright
import os


# ====== FUNÇÃO AUXILIAR PARA SALVAR DOWNLOADS ======

def salvar_download(download, nome_final: str):
    """
    Salva o arquivo baixado dentro da pasta 'downloads' com o nome desejado.
    """
    os.makedirs("downloads", exist_ok=True)
    destino = os.path.join("downloads", nome_final)

    print(f"Salvando arquivo em: {destino}")
    download.save_as(destino)


# ====== ETAPA 1 — ABRIR SISTEMA E PROJETO ======

def abrir_unifier(page, base_url: str):
    """
    Abre o Primavera Unifier (GCMS) na URL base.
    Considera que já estamos dentro da rede Alcoa (sem login).
    """
    print(f"Abrindo GCMS em: {base_url}")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    print("GCMS carregado.")


def abrir_projeto(page, numero_projeto: str):
    """
    Clicar no '+' → pesquisar pelo número do projeto → abrir o projeto.
    """
    print(f"Abrindo projeto: {numero_projeto}")

    # Ícone de "+" no topo (selector genérico – ajuste se necessário)
    page.get_by_role("button", name="+").click()

    # Campo "Pesquisar por nome ou número..."
    page.get_by_placeholder("Pesquisar por nome ou número").fill(numero_projeto)

    # Espera um pouco para aparecer o resultado
    page.wait_for_timeout(1000)

    # Clicar na linha que contém o número do projeto
    page.get_by_text(numero_projeto, exact=False).click()

    # Espera carregar o workspace do projeto
    page.wait_for_load_state("networkidle")
    print("Projeto aberto.")


# ====== ETAPA 2 — COST SHEET: PROJECT COST SHEET ======

def baixar_cost_sheet(page, numero_projeto: str):
    """
    Finance → Cost Sheet → Project Cost Sheet → Export to CSV.
    Gera: CostSheet_{NumeroProjeto}.csv
    """
    print("Indo para Finance → Cost Sheet...")

    # Menu Finance no lado esquerdo
    page.get_by_text("Finance", exact=True).click()

    # Submenu Cost Sheet
    page.get_by_text("Cost Sheet", exact=True).click()
    page.wait_for_load_state("networkidle")

    # Duplo clique em "Project Cost Sheet"
    print("Abrindo 'Project Cost Sheet'...")
    page.get_by_text("Project Cost Sheet", exact=False).dblclick()
    page.wait_for_load_state("networkidle")

    # Botão de Print/Export (ícone de impressora/export)
    print("Abrindo menu de exportação do Cost Sheet...")
    # Aqui usamos o título do botão; ajuste se for diferente
    page.get_by_role("button", name="Print").click()

    # Selecionar "Export To CSV"
    page.get_by_text("Export To CSV", exact=True).click()

    print("Aguardando download do Cost Sheet...")
    download = page.wait_for_event("download")
    nome_final = f"CostSheet_{numero_projeto}.csv"
    salvar_download(download, nome_final)
    print("Cost Sheet baixado.")


# ====== ETAPA 3 — CASH FLOW: ACTUALS vs BASELINE ======

def baixar_cashflow_actuals(page, numero_projeto: str):
    """
    Finance → Cash Flow → Actuals vs Baseline → Export to CSV (Actuals).
    Gera: CashFlow_Actuals_{NumeroProjeto}.csv
    """
    print("Indo para Finance → Cash Flow (Actuals vs Baseline)...")

    # Menu Cash Flow
    page.get_by_text("Cash Flow", exact=True).click()
    page.wait_for_load_state("networkidle")

    # Duplo clique em "Actuals vs Baseline"
    print("Abrindo 'Actuals vs Baseline'...")
    page.get_by_text("Actuals vs Baseline", exact=False).dblclick()
    page.wait_for_load_state("networkidle")

    # Painel de curvas (All Curves) → três pontinhos
    print("Abrindo menu de curvas (três pontinhos)...")
    # Selector genérico para os "..." (pode precisar de ajuste fino)
    page.get_by_role("button", name="More options").click()

    # Selecionar "Actuals"
    print("Selecionando curva 'Actuals'...")
    page.get_by_text("Actuals", exact=False).click()

    # Botão de exportação (ícone de download)
    print("Exportando 'Actuals vs Baseline' para CSV...")
    page.get_by_role("button", name="Export").click()
    page.get_by_text("Export To CSV", exact=True).click()

    print("Aguardando download do Cash Flow Actuals...")
    download = page.wait_for_event("download")
    nome_final = f"CashFlow_Actuals_{numero_projeto}.csv"
    salvar_download(download, nome_final)
    print("Cash Flow Actuals baixado.")

    # Fechar aba interna (X)
    print("Fechando aba de 'Actuals vs Baseline'...")
    page.get_by_role("button", name="Close").click()


# ====== ETAPA 4 — CASH FLOW: FORECAST (Cash Flow by CBS) ======

def baixar_cashflow_forecast(page, numero_projeto: str):
    """
    Finance → Cash Flow → Cash Flow by CBS → Forecast → Export to CSV.
    Gera: CashFlow_Forecast_{NumeroProjeto}.csv
    """
    print("Indo para 'Cash Flow by CBS'...")

    # Estando ainda em Cash Flow, tela de lista
    page.get_by_text("Cash Flow by CBS", exact=False).dblclick()
    page.wait_for_load_state("networkidle")

    # Painel de curvas → três pontinhos
    print("Abrindo menu de curvas (três pontinhos) para Forecast...")
    page.get_by_role("button", name="More options").click()

    # Selecionar "Forecast"
    print("Selecionando curva 'Forecast'...")
    page.get_by_text("Forecast", exact=False).click()

    # Botão de exportação
    print("Exportando 'Cash Flow by CBS - Forecast' para CSV...")
    page.get_by_role("button", name="Export").click()
    page.get_by_text("Export To CSV", exact=True).click()

    print("Aguardando download do Cash Flow Forecast...")
    download = page.wait_for_event("download")
    nome_final = f"CashFlow_Forecast_{numero_projeto}.csv"
    salvar_download(download, nome_final)
    print("Cash Flow Forecast baixado.")

    # Fechar aba interna (X)
    print("Fechando aba de 'Cash Flow by CBS'...")
    page.get_by_role("button", name="Close").click()


# ====== FUNÇÃO PRINCIPAL PARA UM PROJETO ======

def executar_fluxo(numero_projeto: str, base_url: str):
    """
    Executa o fluxo completo para UM projeto:
    - abre GCMS
    - abre projeto
    - baixa Cost Sheet
    - baixa Cash Flow Actuals
    - baixa Cash Flow Forecast
    """
    print("=" * 80)
    print(f"Iniciando fluxo para o projeto: {numero_projeto}")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        abrir_unifier(page, base_url)
        abrir_projeto(page, numero_projeto)
        baixar_cost_sheet(page, numero_projeto)
        baixar_cashflow_actuals(page, numero_projeto)
        baixar_cashflow_forecast(page, numero_projeto)

        browser.close()
        print(f"Fluxo concluído para o projeto: {numero_projeto}")
