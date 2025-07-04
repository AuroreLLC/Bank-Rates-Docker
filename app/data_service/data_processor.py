# data_processor.py
"""
Data processing module for Banking Rates Dashboard
Handles all data fetching, transformation, and caching operations
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import streamlit as st

from constants.fred import FRED_SERIES_REGISTRY
from data_service.fetchers.fetch_rates import FredSeries
from data_service.scrapers.fhlb_scraper import FHLBScraper
from data_service.scrapers.farmer_mac import FarmerMacScraper


class DataProcessor:
    """Main data processing class for banking rates"""
    
    def __init__(self, fred_api_key: str, fred_base_url: str):
        self.fred_series = FredSeries(fred_api_key, fred_base_url)
        self.fhlb_scraper = FHLBScraper(wait_time=1)
        self.farm_mac_scraper = FarmerMacScraper(wait_time=1)
    
    @st.cache_data
    def load_fred_summary(_self) -> Tuple[pd.DataFrame, str]:
        """Load and cache FRED summary data"""
        records = []
        for name, meta in FRED_SERIES_REGISTRY.items():
            df = _self.fred_series.run_pipeline(meta['series_id'])
            source_url = meta['source']
            
            if not df.empty:
                latest = df.index.max()
                val = df.loc[latest, 'value']
                records.append({
                    'Rate Name': name,
                    'Latest Date': latest.strftime('%Y-%m-%d'),
                    'Latest Value': round(val, 2),
                    'Source': source_url
                })
            else:
                records.append({
                    'Rate Name': name,
                    'Latest Date': 'N/A',
                    'Latest Value': 'No Data',
                    'Source': source_url
                })
        
        return pd.DataFrame(records), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_combined_rate_summary(self) -> Tuple[pd.DataFrame, str]:
        """Get combined summary including custom rates"""
        records = []
        
        # Start with cached base summary
        fred_df, fetch_time = self.load_fred_summary()
        records.extend(fred_df.to_dict("records"))
        
        # Add custom rates from session state
        if 'custom_rates' in st.session_state:
            for custom_name, series in st.session_state.custom_rates.items():
                if not series.empty:
                    latest = series.index.max()
                    val = series.loc[latest]
                    records.append({
                        'Rate Name': custom_name,
                        'Latest Date': latest.strftime('%Y-%m-%d'),
                        'Latest Value': round(val, 2),
                        'Source': 'User-defined custom rate'
                    })
        
        return pd.DataFrame(records), fetch_time
    
    @st.cache_data
    def load_fred_series(_self, series_id: str) -> pd.DataFrame:
        """Load specific FRED series data"""
        df = _self.fred_series.run_pipeline(series_id)
        if not df.empty:
            df.index = pd.to_datetime(df.index)
        return df
    
    @st.cache_data
    def load_fhlb_data(_self) -> Dict:
        """Load FHLB rates data"""
        rates = _self.fhlb_scraper.run_pipeline()
        return rates
    
    @st.cache_data
    def load_farm_mac_data(_self) -> Tuple[Dict, str]:
        """Load Farmer Mac COFI data"""
        df_yearly, df_3_months = _self.farm_mac_scraper.run_pipeline()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "yearly_resets": df_yearly, 
            "monthly_3month_cofi": df_3_months
        }, timestamp


class CustomRateBuilder:
    """Handles custom rate calculations and operations"""
    
    def __init__(self, data_processor: DataProcessor):
        self.data_processor = data_processor
    
    def create_simple_custom_rate(self, base_rate: str, operation: str, 
                                 custom_value: float) -> Tuple[pd.Series, str]:
        """Create simple custom rate with single operation"""
        series_id = FRED_SERIES_REGISTRY[base_rate]['series_id']
        base_df = self.data_processor.fred_series.run_pipeline(series_id)
        
        if base_df.empty:
            return pd.Series(), ""
        
        label_map = {
            "Add": "+", "Subtract": "-", "Multiply": "*", "Divide": "/"
        }
        symbol = label_map[operation]
        rate_name = f"{base_rate} {symbol} {custom_value}"
        
        if operation == "Add":
            custom_series = base_df['value'] + custom_value
        elif operation == "Subtract":
            custom_series = base_df['value'] - custom_value
        elif operation == "Multiply":
            custom_series = base_df['value'] * custom_value
        elif operation == "Divide":
            custom_series = base_df['value'] / custom_value
        
        return custom_series, rate_name
    
    def create_weighted_custom_rate(self, components: List[Tuple[str, float]]) -> Tuple[pd.Series, str]:
        """Create weighted combination of multiple rates"""
        series_data = []
        
        for rate_name, weight in components:
            series_id = FRED_SERIES_REGISTRY[rate_name]['series_id']
            df = self.data_processor.fred_series.run_pipeline(series_id)
            if not df.empty:
                series_data.append((df['value'], weight / 100.0, rate_name))
        
        if not series_data:
            return pd.Series(), ""
        
        # Use first series as base index
        base_index = series_data[0][0].index
        custom_series = pd.Series(0.0, index=base_index)
        label = " + ".join([f"{w*100:.0f}% {name}" for _, w, name in series_data])
        
        for series, weight, _ in series_data:
            aligned = series.reindex(base_index).fillna(method='ffill')
            custom_series += aligned * weight
        
        return custom_series, label
    
    def save_custom_rate(self, rate_name: str, custom_series: pd.Series) -> bool:
        """Save custom rate to session state"""
        if 'custom_rates' not in st.session_state:
            st.session_state.custom_rates = {}
        
        st.session_state.custom_rates[rate_name] = custom_series
        return True


class DataFilterer:
    """Handles data filtering and date range operations"""
    
    @staticmethod
    def filter_by_date(df: pd.DataFrame, target_date: pd.Timestamp) -> pd.DataFrame:
        """Filter dataframe by specific date"""
        return df.loc[df.index.date == target_date.date()]
    
    @staticmethod
    def filter_by_date_range(df: pd.DataFrame, start_date: pd.Timestamp, 
                           end_date: pd.Timestamp) -> pd.DataFrame:
        """Filter dataframe by date range"""
        return df.loc[(df.index.date >= start_date.date()) & 
                     (df.index.date <= end_date.date())]
    
    @staticmethod
    def get_monthly_data(df: pd.DataFrame) -> pd.DataFrame:
        """Get monthly data (first day of each month)"""
        return df[df.index.day == 1]
    
    @staticmethod
    def prepare_download_data(df: pd.DataFrame, rate_name: str) -> pd.DataFrame:
        """Prepare data for download with proper formatting"""
        named_df = df.rename(columns={"value": rate_name})
        named_df = named_df.reset_index()
        named_df.columns = ["Date", rate_name]
        named_df["Date"] = named_df["Date"].dt.strftime("%Y-%m")
        return named_df


class CofiDataProcessor:
    """Specialized processor for COFI data transformations"""
    
    @staticmethod
    def process_yearly_cofi(cofi_yearly: pd.DataFrame) -> pd.DataFrame:
        """Process yearly COFI data for visualization"""
        # Convert percentage strings to numeric values
        for col in ['1-Year COFI', '5-Year Reset', '10-Year Reset', '15-Year Reset']:
            cofi_yearly[col] = pd.to_numeric(
                cofi_yearly[col].astype(str).str.replace('%', '', regex=False),
                errors='coerce'
            )
        
        cofi_yearly = cofi_yearly.reset_index()
        cofi_yearly = cofi_yearly.rename(columns={'index': 'Year'})
        
        # Melt for visualization
        df_long = cofi_yearly.melt(
            id_vars='Year',
            value_vars=['1-Year COFI', '5-Year Reset', '10-Year Reset', '15-Year Reset'],
            var_name='Term',
            value_name='Rate'
        )
        
        return df_long
    
    @staticmethod
    def process_monthly_cofi(cofi_3_months: pd.DataFrame) -> pd.DataFrame:
        """Process monthly COFI data for visualization"""
        cofi_3_months = cofi_3_months.copy()
        cofi_3_months['COFI'] = cofi_3_months['3-Month COFI'].str.replace('%', '').astype(float)
        cofi_3_months["Date"] = pd.to_datetime(
            cofi_3_months['Year'] + '-' + cofi_3_months['Month'], 
            format='%Y-%B'
        )
        cofi_3_months = cofi_3_months.sort_values(by='Date')
        return cofi_3_months