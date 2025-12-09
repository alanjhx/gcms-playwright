from playwright.sync_api import sync_playwright

def main():
    print("Iniciando Playwright na nuvem...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        print("Título da página:", page.title())
        browser.close()

    print("Finalizei sem erro.")

if __name__ == "__main__":
    main()
