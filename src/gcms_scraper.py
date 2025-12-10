import os

from pathlib import Path

from typing import Optional

 

from playwright.sync_api import (

    sync_playwright,

    TimeoutError as PlaywrightTimeoutError,

    Page,

)

 

# Pasta onde os arquivos serão salvos dentro do repositório

DOWNLOAD_DIR = Path(os.environ.get("DOWNLOAD_DIR", "downloads"))

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

 

# Senha do GCMS: preferencialmente usar variável de ambiente GCMS_PASSWORD

GCMS_PASSWORD = os.environ.get("GCMS_PASSWORD", "Alcoa1234@")

 

 

# ----------------------------------------------------------------------

# LOGIN

# ----------------------------------------------------------------------

def garantir_login(page: Page) -> None:

    print("Página do GCMS carregada.")

    print("Verificando se é necessário fazer login...")

 

    # 1) Tela de senha

    try:

        if page.locator("input[type='password']").count() > 0:

            print("Tela de senha detectada. Preenchendo senha...")

            campo_senha = page.locator("input[type='password']").first

            campo_senha.fill(GCMS_PASSWORD)

 

            botao_entrar = page.get_by_role("button", name="Entrar")

            if botao_entrar.count() == 0:

                print("[ERRO] Botão 'Entrar' não encontrado.")

            else:

                botao_entrar.click()

 

            page.wait_for_load_state("networkidle", timeout=30000)

        else:

            print("Nenhum campo de senha visível.")

    except PlaywrightTimeoutError:

        print("[AVISO] Timeout ao tentar preencher a senha.")

 

    # 2) Tela "Continuar conectado?"

    try:

        if page.locator("text=Continuar conectado?").count() > 0:

            print("Tela 'Continuar conectado?' detectada. Clicando 'Não'...")

            botao_nao = page.get_by_role("button", name="Não")

            if botao_nao.count() > 0:

                botao_nao.click()

                page.wait_for_load_state("networkidle", timeout=30000)

            else:

                print("[AVISO] Botão 'Não' não encontrado.")

        else:

            print("Tela 'Continuar conectado?' não apareceu.")

    except PlaywrightTimeoutError:

        print("[AVISO] Timeout ao tratar a tela 'Continuar conectado?'.")

 

    print("Login concluído.")

 

 

# ----------------------------------------------------------------------

# NAVEGAÇÃO BÁSICA: ABRIR PROJETO

# ----------------------------------------------------------------------

def abrir_projeto(page: Page, numero_projeto: str) -> bool:

    print(f"Abrindo projeto: {numero_projeto}")

 

    # Botão "+"

    botao_mais = page.locator("oj-button[Id="openTabsBtn"] > button > div > span > span")

    if botao_mais.count() == 0:

        print("[ERRO] Botão '+' (openTabsBtn) não encontrado. Pulando projeto.")

        return False

 

    try:

        botao_mais.click()

    except PlaywrightTimeoutError:

        print("[ERRO] Timeout ao clicar no botão '+'.")

        return False

 

    # Campo de pesquisa

    try:

        campo_pesquisa = page.locator(

            "xpath=//*[@id='searchInputContainer_inputSearchString']/div/input"

        )

        campo_pesquisa.wait_for(timeout=15000)

        campo_pesquisa.fill(numero_projeto)

    except PlaywrightTimeoutError:

        print("[ERRO] Campo de pesquisa de projeto não encontrado.")

        return False

 

    # Resultado da pesquisa

    try:

        resultado = page.locator(

            f"xpath=//oj-list-item-layout[contains(., '{numero_projeto}')]"

        )

        resultado.first.wait_for(timeout=15000)

    except PlaywrightTimeoutError:

        print(f"[AVISO] Projeto {numero_projeto} não encontrado na pesquisa.")

        return False

 

    try:

        resultado.first.click()

        page.wait_for_load_state("networkidle", timeout=30000)

        print(f"Projeto {numero_projeto} aberto com sucesso.")

        return True

    except PlaywrightTimeoutError:

        print(f"[ERRO] Timeout ao abrir o projeto {numero_projeto}.")

        return False

 

 

# ----------------------------------------------------------------------

# HELPERS DE NAVEGAÇÃO NO MENU ESQUERDO

# ----------------------------------------------------------------------

def clicar_menu(page: Page, texto: str) -> bool:

    """Clica em um item de menu (esquerda) por texto visível."""

    locator = page.locator(f"xpath=//span[contains(text(), '{texto}')]")

    if locator.count() == 0:

        print(f"[ERRO] Item de menu '{texto}' não encontrado.")

        return False

    try:

        locator.first.click()

        page.wait_for_load_state("networkidle", timeout=30000)

        return True

    except PlaywrightTimeoutError:

        print(f"[ERRO] Timeout ao clicar no menu '{texto}'.")

        return False

 

 

# ----------------------------------------------------------------------

# HELPER DE DOWNLOAD (Export To CSV / Excel)

# ----------------------------------------------------------------------

def _fazer_download_export(page: Page, nome_arquivo_saida: str) -> Optional[Path]:

    """Clica em Export e escolhe Export To CSV (ou Excel) salvando com nome_arquivo_saida."""

    # Botão de export

    botao_export = page.locator("xpath=//*[@id='exportdetails']//button")

    if botao_export.count() == 0:

        print("[ERRO] Botão de exportação (exportdetails) não encontrado.")

        return None

 

    try:

        botao_export.click()

    except PlaywrightTimeoutError:

        print("[ERRO] Timeout ao clicar no botão de exportação.")

        return None

 

    # Opção Export To CSV / Excel

    opcao_csv = page.locator("text=Export To CSV")

    opcao_excel = page.locator("text=Export To Excel")

 

    target = None

    if opcao_csv.count() > 0:

        target = opcao_csv.first

    elif opcao_excel.count() > 0:

        target = opcao_excel.first

    else:

        print("[ERRO] Nenhuma opção 'Export To CSV' ou 'Export To Excel' encontrada.")

        return None

 

    try:

        with page.expect_download(timeout=60000) as download_info:

            target.click()

        download = download_info.value

        destino = DOWNLOAD_DIR / nome_arquivo_saida

        download.save_as(destino)

        print(f"[OK] Download salvo em: {destino}")

        return destino

    except PlaywrightTimeoutError:

        print("[ERRO] Timeout aguardando o download.")

        return None

    except Exception as e:

        print(f"[ERRO] Falha ao salvar o download: {e}")

        return None

 

 

# ----------------------------------------------------------------------

# COST SHEET

# ----------------------------------------------------------------------

def baixar_cost_sheet(page: Page, numero_projeto: str) -> None:

    print("=== ETAPA: COST SHEET ===")

 

    if not clicar_menu(page, "Finance"):

        print("[ERRO] Não foi possível entrar em Finance.")

        return

 

    if not clicar_menu(page, "Cost Sheet"):

        print("[ERRO] Não foi possível entrar em Cost Sheet.")

        return

 

    # Linha "Project Cost Sheet"

    linha_project_cost = page.locator(

        "xpath=//div[contains(@class,'cell-renderer') and contains(text(),'Project Cost Sheet')]"

    )

    if linha_project_cost.count() == 0:

        print("[ERRO] Linha 'Project Cost Sheet' não encontrada.")

        return

 

    try:

        linha_project_cost.first.dblclick()

        page.wait_for_load_state("networkidle", timeout=30000)

    except PlaywrightTimeoutError:

        print("[ERRO] Timeout ao abrir 'Project Cost Sheet'.")

        return

 

    # Exportar

    nome_saida = f"CostSheet_{numero_projeto}.csv"

    _fazer_download_export(page, nome_saida)

 

    # Fechar aba interna (se existir)

    botao_fechar = page.locator("xpath=//*[@id='closecfsheet']/button/div")

    if botao_fechar.count() > 0:

        try:

            botao_fechar.first.click()

        except PlaywrightTimeoutError:

            print("[AVISO] Timeout ao tentar fechar a aba Cost Sheet.")

 

 

# ----------------------------------------------------------------------

# CASH FLOW – ACTUALS VS BASELINE

# ----------------------------------------------------------------------

def baixar_cashflow_actual_vs_baseline(page: Page, numero_projeto: str) -> None:

    print("=== ETAPA: CASH FLOW – Actuals vs Baseline ===")

 

    if not clicar_menu(page, "Finance"):

        print("[ERRO] Não foi possível entrar em Finance.")

        return

 

    if not clicar_menu(page, "Cash Flow"):

        print("[ERRO] Não foi possível entrar em Cash Flow.")

        return

 

    # Linha "Actuals vs Baseline"

    linha_actuals_vs_baseline = page.locator(

        "xpath=//div[contains(@class,'cell-renderer') and contains(text(),'Actuals vs Baseline')]"

    )

    if linha_actuals_vs_baseline.count() == 0:

        print("[ERRO] Linha 'Actuals vs Baseline' não encontrada.")

        return

 

    try:

        linha_actuals_vs_baseline.first.dblclick()

        page.wait_for_load_state("networkidle", timeout=30000)

    except PlaywrightTimeoutError:

        print("[ERRO] Timeout ao abrir 'Actuals vs Baseline'.")

        return

 

    # Trema (inner splitter) – expande painel de curvas

    trema = page.locator("xpath=//a[@aria-label='inner-splitter']")

    if trema.count() > 0:

        try:

            trema.first.click()

        except PlaywrightTimeoutError:

            print("[AVISO] Timeout ao clicar no trema (Actuals vs Baseline).")

    else:

        print("[AVISO] Trema não encontrado (Actuals vs Baseline).")

 

    # Selecionar "Actuals" (opcional – se não encontrar, segue igual)

    actuals_link = page.locator(

        "xpath=//a[contains(@title,'Click to open the link') and contains(.,'Actuals')]"

    )

    if actuals_link.count() > 0:

        try:

            actuals_link.first.click()

        except PlaywrightTimeoutError:

            print("[AVISO] Timeout ao selecionar 'Actuals'.")

    else:

        print("[AVISO] Linha 'Actuals' não encontrada — exportando mesmo assim.")

 

    nome_saida = f"CashFlow_Actuals_{numero_projeto}.csv"

    _fazer_download_export(page, nome_saida)

 

    # Fechar aba interna

    botao_fechar = page.locator("xpath=//*[@id='closecfsheet']/button/div")

    if botao_fechar.count() > 0:

        try:

            botao_fechar.first.click()

        except PlaywrightTimeoutError:

            print("[AVISO] Timeout ao fechar aba de Cash Flow (Actuals vs Baseline).")

 

 

# ----------------------------------------------------------------------

# CASH FLOW – CASH FLOW BY CBS

# ----------------------------------------------------------------------

def baixar_cashflow_by_cbs(page: Page, numero_projeto: str) -> None:

    print("=== ETAPA: CASH FLOW – Cash Flow by CBS ===")

 

    if not clicar_menu(page, "Finance"):

        print("[ERRO] Não foi possível entrar em Finance.")

        return

 

    if not clicar_menu(page, "Cash Flow"):

        print("[ERRO] Não foi possível entrar em Cash Flow.")

        return

 

    # Linha "Cash Flow by CBS"

    linha_cbs = page.locator(

        "xpath=//div[contains(@class,'cell-renderer') and contains(text(),'Cash Flow by CBS')]"

    )

    if linha_cbs.count() == 0:

        print("[ERRO] Linha 'Cash Flow by CBS' não encontrada.")

        return

 

    try:

        linha_cbs.first.dblclick()

        page.wait_for_load_state("networkidle", timeout=30000)

    except PlaywrightTimeoutError:

        print("[ERRO] Timeout ao abrir 'Cash Flow by CBS'.")

        return

 

    # Trema – expande painel de curva


