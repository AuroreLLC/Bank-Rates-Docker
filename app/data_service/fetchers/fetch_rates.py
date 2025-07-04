# utils/fetch_rates.py
import os
import logging

from typing import Optional, Dict

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv


load_dotenv()
g_logger = logging.getLogger(__name__)

class FredSeries:
    def __init__(self, api_key: str, url: str):
        self.api_key = api_key
        self.source = url
        self.session= requests.Session()
        _retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=_retry_strategy))
        self.session.mount('http://', HTTPAdapter(max_retries=_retry_strategy))

    def _generate_params(self, start_date: str,series_id:str) -> Dict[str, str]:
        params = {
        'series_id': series_id,
        'api_key': self.api_key,
        'file_type': 'json',
        'observation_start': start_date,
        }
        return params
    
    def _is_env_valid(self):
        if not self.api_key:
            print("FRED_API_KEY is not set in environment.")
            return False
        if not self.source:
            print("Source URL is not set.")
            return False
        return True

    def _fetch_data(self, url:str,params: Optional[Dict] = None) -> Optional[dict]:
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            g_logger.error("Request to %s failed: %s", url, err)
        except ValueError as err:
            g_logger.error("Invalid JSON from %s: %s", url, err)
        return None
    
    def _process_data(self, payload: dict) -> pd.DataFrame:

        observations = payload.get('observations', [])
        if not observations:
            g_logger.warning(
                "No observations returned for series '%s' from %s.", self.source, self.source
            )
            return pd.DataFrame()

        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.set_index('date').sort_index()

        return df[['value']]
    
    def run_pipeline(self,series_id: str,start_date: str = '2020-01-01') -> pd.DataFrame:

        if not self._is_env_valid():
            return pd.DataFrame()
        
        params = self._generate_params(start_date,series_id)
        payload = self._fetch_data(self.source, params)
        processed_data = self._process_data(payload)
        g_logger.info(f"Data fetched and processed successfully. For series {series_id}")
        return processed_data




