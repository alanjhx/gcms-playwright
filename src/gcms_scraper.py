# src/gcms_scraper.py
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

GCMS_PASSWORD = os.environ.get("GCMS_PASSWORD", "")
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def patch_oracle_jet(page):
    # Remove limitações do headless, força animações e shadow DOM a carregarem
    page.add_init_script("""
        window.requestAnimationFrame = (cb) => cb();
    """)
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => false});
    """)
    page.add_init_script("""
        HTMLElement.prototype.animate = function() { return {finished: Promise.resolve()}; };
    """)


def wait_render(page):
    page.wait_for_load_state("domcontentloaded")
    try:
        page.locator("oj-progress-circle").wait_for(state="hidden", timeout=5000)
    except:
        pass
    page.wait_for_timeout(800)


def deep_click(page, selector):
    """
    Procura elemento dentro de shadowRoot e clica.
    """
    handle = page.evaluate_handle(
        """(sel) => {
            function find(root) {
                let el = root.querySelector(sel);
                if (el) return el;
                for (const child of root.children) {
                    if (child.shadowRoot) {
                        let r = find(child.shadowRoot);
                        if (r) return r;
                    }
                    let r2 = find(child);
                    if (r2) return r2;
                }
                return null;
            }
            return find(document);
        }""",
        selector,
    )

    if handle.json_value() is None:
        return False

    page.evaluate("(el)=>el.scrollIntoView()", handle)
    page.wait_for_timeout(300)
    page.evaluate("(el)=>el.click()", handle)
    page.wait_for_timeout(800)
    return True


def login_if_needed(page):
    # Senha
    if page.locator("input[type='password']").count() > 0:
        field = page.locator("input[type='password']").first
        field.fill(GCMS_PASSWORD)
        if page.locator("button:has-text('Entrar')").count() > 0:
            page.locator("button:has-text('Entrar')").click()
        wait_render(page)

    # Continuar conectado?
    if page.locator("button:has-text('Não')").count() > 0:
        page.locator("button:has-text('Não')").click()
        wait_render(page)


def abrir_projeto(page, projeto):
    print(f"[abrir] {projeto}")

    # Botão "+"
    if not deep_click(page, "#openTabsBtn > button"):
        print("Botão '+' não encontrado.")
        return False

    # Campo de pesquisa
    field = page.locator("xpath=//*[@id='searchInputContainer_inputSearchString']/div/input")
    try:
        field.wait_for(timeout=8000)
    except:
        print("Campo de pesquisa não apareceu.")
        return False

    field.fill(projeto)
    page.keyboard.press("Enter")
    wait_render(page)

    # Selecionar resultado
    item = page.locator(f"xpath=//oj-list-item-layout[contains(., '{projeto}')]")
    if item.count() == 0:
        print("Projeto não encontrado na pesquisa.")
        return False

    item.first.click()
    wait_render(page)
    return True


def exportar(page, nomesaida):
    # deep search export button
    if not deep_click(page, "#exportdetails button"):
        # fallback
        if page.locator("xpath=//*[@id='exportdetails']//button").count() > 0:
            page.locator("xpath=//*[@id='exportdetails']//button").click()
        else:
            print("Botão export não encontrado.")
            return

    page.wait_for_timeout(600)

    opcao = None
    if page.locator("text=Export To CSV").count() > 0:
        opcao = page.locator("text=Export To CSV").first
    elif page.locator("text=Export To Excel").count() > 0:
        opcao = page.locator("text=Export To Excel").first
    else:
        print("Nenhuma opção de export encontrada.")
        return

    with page.expect_download(timeout=60000) as dlinfo:
        opcao.click()

    download = dlinfo.value
    destino = DOWNLOAD_DIR / nomesaida
    download.save_as(destino)
    print(f"Salvo: {destino}")


def executar_fluxo(projeto, base_url):
    print(f"\n=== Executando {projeto} ===")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=False,              # OBRIGATÓRIO para render JET
            args=["--no-sandbox"]
        )

        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        patch_oracle_jet(page)

        page.goto(base_url, timeout=90000)
        wait_render(page)
        login_if_needed(page)

        # Abre projeto
        if not abrir_projeto(page, projeto):
            context.close()
            browser.close()
            return False

        # Finance > Cost Sheet
        try:
            page.locator("text=Finance").first.click()
            wait_render(page)

            page.locator("text=Cost Sheet").first.click()
            wait_render(page)

            page.locator("text=Project Cost Sheet").first.dblclick()
            wait_render(page)

            exportar(page, f"CostSheet_{projeto}.csv")
        except Exception as e:
            print("Erro CostSheet:", e)

        # Finance > Cash Flow > Actuals vs Baseline
        try:
            page.locator("text=Finance").first.click()
            wait_render(page)

            page.locator("text=Cash Flow").first.click()
            wait_render(page)

            page.locator("text=Actuals vs Baseline").first.dblclick()
            wait_render(page)

            deep_click(page, "a[aria-label='inner-splitter']")

            exportar(page, f"Actuals_{projeto}.csv")
        except Exception as e:
            print("Erro Actuals:", e)

        context.close()
        browser.close()
        return True
