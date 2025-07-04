from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from data_service.scrapers.web_driver import WebDriverContext
from bs4 import BeautifulSoup
import pandas as pd
import time

class FarmerMacScraper():
    def __init__(self, wait_time=1):
        self.wait_time = wait_time

    def get_page(self, driver, url = "https://www.farmermac.com/cofi/"):
        driver.get(url)
        time.sleep(self.wait_time)
        return driver.page_source
    
    def extract_data(self, html):
        soup = BeautifulSoup(html, "html.parser")
        headers = [th.get_text(strip=True) for th in soup.find_all('th')]
        data_rows = []
        for row in soup.find_all('tbody')[0].find_all('tr'):
            cols = [td.get_text(strip=True) for td in row.find_all('td')]
            data_rows.append(dict(zip(headers, cols)))
        return data_rows

    def parse_data(self,data_raw):
        data = self.process_data(data_raw)
        yearly_resets = self.get_yearly_data(data) 
        monthly_3month_cofi = self.get_monthly_data(data) 
        return {
            'yearly_resets': yearly_resets,
            'monthly_3month_cofi': monthly_3month_cofi
        }

    def process_data(self,data):
        current_year = ""
        for row in data:
            if row["Year"]:
                current_year = row["Year"]
            else:
                row["Year"] = current_year
        return data

    def get_yearly_data(self,data):
        yearly_resets = {}
        for row in data:
            year = row["Year"]
            if year not in yearly_resets and row["1-Year COFI"]:
                yearly_resets[year] = {
                    "1-Year COFI": row["1-Year COFI"],
                    "5-Year Reset": row["5-Year Reset"],
                    "10-Year Reset": row["10-Year Reset"],
                    "15-Year Reset": row["15-Year Reset"]
                }
        return yearly_resets

    def get_monthly_data(self,data):
        monthly_3month_cofi = []
        for row in data:
            if row["3-Month COFI*"]:
                monthly_3month_cofi.append({
                    "Year": row["Year"],
                    "Month": row["Month"],
                    "3-Month COFI": row["3-Month COFI*"]
                })
        return monthly_3month_cofi
    
    def generate_dataframes(self, data):
        df_yearly = pd.DataFrame(data['yearly_resets']).T
        df_monthly = pd.DataFrame(data['monthly_3month_cofi'])
        return df_yearly, df_monthly
    
    def run_pipeline(self):
        with WebDriverContext(headless=True) as driver:
            url = "https://www.farmermac.com/cofi/"
            html = self.get_page(driver, url)
        data_raw = self.extract_data(html)
        data = self.parse_data(data_raw)
        df_yearly, df_monthly = self.generate_dataframes(data)
        return df_yearly, df_monthly

