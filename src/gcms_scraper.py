import os
from pathlib import Path
from typing import Optional
 
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Page,
)
 
DOWNLOAD_DIR = Path(os.environ.get("DOWNLOAD_DIR", "downloads"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
 
GCMS_PASSWORD = os.environ.get("GCMS_PASSWORD", "Alcoa1234@")
 
 
# ----------------------------------------------------------------------
# Função essencial — espera Oracle JET renderizar
# ----------------------------------------------------------------------
def aguardar_render(page: Page, timeout=40000):
    """
    Aguarda o Oracle JET renderizar o conteúdo após cada clique.
    """
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
 
        spinners = page.locator(
            "oj-progress-circle, .oj-progress-bar, .oj-busy-state, .oj-busy-context"
        )
 
        if spinners.count() > 0:
            try:
                spinners.first.wait_for(state="hidden", timeout=timeout)
            except:
                pass
 
        page.wait_for_timeout(700)
        return True
    except:
        return False
 
 
# ----------------------------------------------------------------------
# LOGIN
# ----------------------------------------------------------------------
def garantir_login(page: Page) -> None:
    print("Verificando login...")
 
    # Tela de senha
    if page.locator("input[type='password']").count() > 0:
        print("Tela de senha detectada. Logando...")
        page.locator("input[type='password']").fill(GCMS_PASSWORD)
 
        btn = page.get_by_role("button", name="Entrar")
        if btn.count() > 0:
            btn.click()
        aguardar_render(page)
 
    # Tela "Continuar conectado?"
    if page.locator("button:has-text('Não')").count() > 0:
        print("Tela 'Continuar conectado?' detectada — clicando NÃO.")
        page.get_by_role("button", name="Não").click()
        aguardar_render(page)
 
    print("Login concluído.")
 
 
# ----------------------------------------------------------------------
# ABRIR PROJETO
# ----------------------------------------------------------------------
def abrir_projeto(page: Page, numero_projeto: str) -> bool:
    print(f"Abrindo projeto: {numero_projeto}")
 
    # Botão "+"
    botao_mais = page.locator("xpath=//*[@id='openTabsBtn']/button")
    if botao_mais.count() == 0:
        print("[ERRO] Botão '+' não encontrado.")
        return False
 
    botao_mais.click()
    aguardar_render(page)
 
    # Campo de busca
    campo = page.locator(
        "xpath=//*[@id='searchInputContainer_inputSearchString']/div/input"
    )
    if campo.count() == 0:
        print("[ERRO] Campo de pesquisa não encontrado.")
        return False
 
    campo.fill(numero_projeto)
    page.keyboard.press("Enter")
    aguardar_render(page)
 
    # Resultado
    resultado = page.locator(
        f"xpath=//oj-list-item-layout[contains(., '{numero_projeto}')]"
    )
 
    if resultado.count() == 0:
        print(f"[AVISO] Projeto {numero_projeto} não encontrado.")
        return False
 
    resultado.first.click()
    aguardar_render(page)
 
    print(f"[OK] Projeto {numero_projeto} aberto.")
    return True
 
 
# ----------------------------------------------------------------------
# MENU ESQUERDO
# ----------------------------------------------------------------------
def clicar_menu(page: Page, texto: str) -> bool:
    locator = page.locator(f"xpath=//span[contains(text(), '{texto}')]")
    if locator.count() == 0:
        print(f"[ERRO] Menu '{texto}' não encontrado.")
        return False
 
    locator.first.click()
    aguardar_render(page)
    return True
 
 
# ----------------------------------------------------------------------
# DOWNLOAD HELPER
# ----------------------------------------------------------------------
def _baixar_export(page: Page, nome_saida: str) -> Optional[Path]:
    botao_export = page.locator("xpath=//*[@id='exportdetails']//button")
    if botao_export.count() == 0:
        print("[ERRO] Botão de exportação não encontrado.")
        return None
 
    with page.expect_download(timeout=60000) as info:
        botao_export.click()
        aguardar_render(page)
 
        opcao = page.locator("text=Export To CSV")
        if opcao.count() == 0:
            opcao = page.locator("text=Export To Excel")
 
        if opcao.count() == 0:
            print("[ERRO] Nenhuma opção de exportação encontrada.")
            return None
 
        opcao.first.click()
 
    download = info.value
    destino = DOWNLOAD_DIR / nome_saida
    download.save_as(destino)
 
    print(f"[OK] Arquivo salvo: {destino}")
    return destino
 
 
# ----------------------------------------------------------------------
# COST SHEET
# ----------------------------------------------------------------------
def baixar_cost_sheet(page: Page, numero: str):
    print("=== COST SHEET ===")
 
    if not clicar_menu(page, "Finance"):
        return
 
    if not clicar_menu(page, "Cost Sheet"):
        return
 
    linha = page.locator(
        "xpath=//div[contains(@class,'cell-renderer') and contains(text(),'Project Cost Sheet')]"
    )
 
    if linha.count() == 0:
        print("[ERRO] Linha 'Project Cost Sheet' não encontrada.")
        return
 
    linha.first.dblclick()
    aguardar_render(page)
 
    _baixar_export(page, f"CostSheet_{numero}.csv")
 
    fechar(page)
 
 
# ----------------------------------------------------------------------
# CASH FLOW – ACTUALS VS BASELINE
# ----------------------------------------------------------------------
def baixar_actual_vs_baseline(page: Page, numero: str):
    print("=== CASH FLOW → Actuals vs Baseline ===")
 
    if not clicar_menu(page, "Finance"):
        return
 
    if not clicar_menu(page, "Cash Flow"):
        return
 
    linha = page.locator(
        "xpath=//div[contains(text(),'Actuals vs Baseline')]"
    )
    if linha.count() == 0:
        print("[ERRO] Linha 'Actuals vs Baseline' não encontrada.")
        return
 
    linha.first.dblclick()
    aguardar_render(page)
 
    # Trema
    trema = page.locator("xpath=//a[@aria-label='inner-splitter']")
    if trema.count() > 0:
        trema.first.click()
        aguardar_render(page)
 
    _baixar_export(page, f"Actuals_{numero}.csv")
 
    fechar(page)
 
 
# ----------------------------------------------------------------------
# CASH FLOW – CASH FLOW BY CBS
# ----------------------------------------------------------------------
def baixar_cashflow_cbs(page: Page, numero: str):
    print("=== CASH FLOW → Cash Flow by CBS ===")
 
    if not clicar_menu(page, "Finance"):
        return
 
    if not clicar_menu(page, "Cash Flow"):
        return
 
    linha = page.locator(
        "xpath=//div[contains(text(),'Cash Flow by CBS')]"
    )
    if linha.count() == 0:
        print("[ERRO] Linha 'Cash Flow by CBS' não encontrada.")
        return
 
    linha.first.dblclick()
    aguardar_render(page)
 
    trema = page.locator("xpath=//a[@aria-label='inner-splitter']")
    if trema.count() > 0:
        trema.first.click()
        aguardar_render(page)
 
    _baixar_export(page, f"CBS_{numero}.csv")
 
    fechar(page)
 
 
# ----------------------------------------------------------------------
# FECHAR ABA INTERNA
# ----------------------------------------------------------------------
def fechar(page: Page):
    btn = page.locator("xpath=//*[@id='closecfsheet']/button")
    if btn.count() > 0:
        btn.first.click()
        aguardar_render(page)
 
 
# ----------------------------------------------------------------------
# EXECUÇÃO DO FLUXO COMPLETO PARA UM PROJETO
# ----------------------------------------------------------------------
def executar_fluxo(numero_projeto: str, base_url: str):
    print(f"\n=============================================")
    print(f"EXECUTANDO PROJETO: {numero_projeto}")
    print(f"=============================================\n")
 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
 
        page.goto(base_url, timeout=60000)
        aguardar_render(page)
 
        garantir_login(page)
 
        if not abrir_projeto(page, numero_projeto):
            print(f"[AVISO] Projeto {numero_projeto} ignorado.")
            return
 
        baixar_cost_sheet(page, numero_projeto)
        baixar_actual_vs_baseline(page, numero_projeto)
        baixar_cashflow_cbs(page, numero_projeto)
 
        context.close()
        browser.close()
 
        print(f"[OK] Projeto {numero_projeto} finalizado.")
