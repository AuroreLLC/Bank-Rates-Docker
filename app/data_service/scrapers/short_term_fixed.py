import pandas as pd
from bs4 import BeautifulSoup
import re
#from scrapers.web_driver import WebDriverContext
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class WebDriverContext:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None

    def __enter__(self):
        options = Options()
        options.headless = self.headless
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless") 
        options.add_argument("--log-level=3") 
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

class FHLBScraper:
    def __init__(self, wait_time=1):
        self.wait_time = wait_time

    def get_page(self, driver, url):
        driver.get(url)
        time.sleep(self.wait_time)
    
    def go_to_short_term_fixed(self,driver ):
        short_term_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#short-term-fixed']")))
        short_term_tab.click()
        time.sleep(1)
        pass

    def extract_html(self, driver):
        return driver.page_source

    def parse_rates(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("#short-term-fixed .table-daily-rates")

        data = []
        if table:
            for row in table.find_all("tr")[2:]:
                #print("Processing row",row)
                cols = row.find_all("td")
                print("Columns found:", len(cols))
                print("------------------------------------------------")
                if len(cols) >= 3:
                    term = cols[0].get_text(strip=True)
                    regular = cols[2].get_text(strip=True)
                    print(f"Term: {term}, Regular Rate: {regular}")
                    if  term and regular and "%" in regular:
                        data.append((term, regular))
        print(data)
        return pd.DataFrame(data, columns=["Term", "Regular Rate (%)"])

    def scrape_rates(self, url="https://www.fhlbc.com/"):
        with WebDriverContext(headless=True) as driver:
            self.get_page(driver, url)
            self.go_to_short_term_fixed(driver)
            html = self.extract_html(driver)
            return self.parse_rates(html)

    def run_pipeline(self):
        return self.scrape_rates()
    
if __name__ == "__main__":
    scraper = FHLBScraper()
    rates = scraper.run_pipeline()
    print(rates)
    