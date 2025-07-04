import pandas as pd
from bs4 import BeautifulSoup
import re
from data_service.scrapers.web_driver import WebDriverContext
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

class FHLBScraper:
    def __init__(self, wait_time=1):
        self.wait_time = wait_time

    def get_page(self, driver, url):
        driver.get(url)
        time.sleep(self.wait_time)
    
    def extract_html(self, driver):
        return driver.page_source
    

    def go_to_short_term_fixed(self,driver,selector ):
        short_term_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,selector)))

        short_term_tab.click()
        time.sleep(1)
        pass

    def parse_rates(self, html,selectors):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one(selectors)
        data = []
        if table:
            for row in table.find_all("tr")[2:]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    term = cols[0].get_text(strip=True)
                    regular = cols[2].get_text(strip=True)
                    if term and regular and "%" in regular:
                        data.append((term, regular))

        return pd.DataFrame(data, columns=["Term", "Regular Rate (%)"])

    def scrape_rates(self, url="https://www.fhlbc.com/"):
        rates = {}
        with WebDriverContext(headless=True) as driver:
            long_term_selectors= "#long-term-fixed .table-daily-rates"
            short_term_selectors = "#short-term-fixed .table-daily-rates"
            short_term_tab_selector =  "//a[@href='#short-term-fixed']"
            self.get_page(driver, url)
            long_term_html = self.extract_html(driver)
            self.go_to_short_term_fixed(driver,short_term_tab_selector)

            short_term_html = self.extract_html(driver)
            long_term_rates = self.parse_rates(long_term_html, long_term_selectors)
            short_term_rates = self.parse_rates(short_term_html, short_term_selectors)
            rates['timestamp'] =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rates['long_term_fixed'] = long_term_rates
            rates['short_term_fixed'] = short_term_rates
            return rates

    def run_pipeline(self):
        return self.scrape_rates()
    