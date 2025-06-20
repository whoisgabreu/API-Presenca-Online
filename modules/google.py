from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from playwright.sync_api import sync_playwright
import os
from time import sleep
import json

class GoogleTransparency():

    def __init__(self):

        self.userData = None
        self.authToken = None

        self.url = 'https://adstransparency.google.com/?hl=pt-BR&region=anywhere'

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--ignore-certificate-errors")
        # self.options.add_argument("--timeout=120")
        self.options.add_argument("--headless=new")
        self.options.add_argument("--window-position=0,0")
        self.options.add_argument("--window-size=800,600")

        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        # self.downloadDir = os.path.join(os.path.expanduser('~'),'Downloads')
        # prefs = {
        #         "profile.default_content_settings.popups": 0,
        #         "download.default_directory": self.downloadDir,
        #         "download.prompt_for_download": False,
        #         "download.directory_upgrade": True
        #         }
        # self.options.add_experimental_option("prefs",prefs)
        # user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data", "Projetos Matriz")
        # self.options.add_argument(f"user-data-dir={user_data_dir}")

    def analyse(self, business_info) -> dict: 
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.url)
        
        self.driver.find_elements(By.CLASS_NAME, "input-area")[0].clear()
        self.driver.find_elements(By.CLASS_NAME, "input-area")[0].send_keys(business_info["empresa"]["razao_social"])

        # WebDriverWait(self.driver, 60).until(EC.visibility_of((By.CSS_SELECTOR, ".ads-count-legacy")))
        sleep(1)

        pres_online = self.driver.execute_script("""
        if (document.querySelector(".ads-count-legacy")) {
            return true;
        } else {
        return false
        }
        """)

        quant_ads = self.driver.execute_script("""
        if (document.querySelector(".ads-count-legacy")) {
            return document.querySelector(".ads-count-legacy").textContent;
        } else {
        return "0"
        }
        """).replace("~", "").split(" ")

        self.driver.quit()

        business_info.setdefault("ads", {}).setdefault("google_transparency", {})

        business_info["ads"]["google_transparency"]["presenca_online"] = pres_online
        business_info["ads"]["google_transparency"]["qtd_anuncio"] = int(quant_ads[0])

        return business_info

class GoogleBusiness:

    def __init__(self):
        self.userData = None
        self.authToken = None
        # self.downloadDir = os.path.join(os.path.expanduser('~'), 'Downloads')

    def analyse(self, business_info) -> dict:

        if business_info["empresa"]["nome_fantasia"] != None:
            print("entrou aqui")
            url = "https://www.google.com/search?q=" + business_info["empresa"]["nome_fantasia"]

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--ignore-certificate-errors",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--window-position=0,0",
                        "--window-size=800,600",
                    ]
                )

                context = browser.new_context(
                    viewport={"width": 800, "height": 600},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    ignore_https_errors=True
                )

                page = context.new_page()

                page.goto(url, timeout=60000)
                sleep(5)  # Se quiser, depois pode trocar por um wait_for_selector

                # -------- Buscar botões com a mesma classe .bkaPDb --------
                botoes = page.query_selector_all(".bkaPDb")
                print(botoes)
                for botao in botoes:
                    span = botao.query_selector("span")
                    if span.inner_text() == "Avaliar":
                        print(span.inner_text())
                        href = botao.query_selector("a").get_attribute("href")
                        new_url = f"https://google.com{href}"

                page.goto(new_url, timeout=60000)

                # -------- Analisar presença e notas --------
                presenca = page.evaluate("""
                    () => {
                        return document.querySelector(".Aq14fc") ? true : false;
                    }
                """)

                nota = page.evaluate("""
                    () => {
                        const el = document.querySelector(".Aq14fc");
                        return el ? parseFloat(el.innerText.replace(",", ".")) : 0;
                    }
                """)

                qtd_avaliacoes = page.evaluate("""
                    () => {
                        const el = document.querySelector(".rjxHPb.PZPZlf span a span");
                        return el ? el.innerText : "0";
                    }
                """)

                # -------- Salvar no dicionário --------
                business_info.setdefault("ads", {}).setdefault("google_business", {})
                business_info["ads"]["google_business"]["presenca_online"] = presenca
                business_info["ads"]["google_business"]["nota"] = nota
                business_info["ads"]["google_business"]["qtd_avaliacao"] = int(qtd_avaliacoes.split(" ")[0])

                browser.close()

        else:
            business_info.setdefault("ads", {}).setdefault("google_business", {})
            business_info["ads"]["google_business"]["presenca_online"] = False
            business_info["ads"]["google_business"]["nota"] = 0
            business_info["ads"]["google_business"]["qtd_avaliacao"] = 0


        return business_info
