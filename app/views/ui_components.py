# ui_components.py
"""
UI components module for Banking Rates Dashboard
Contains all Streamlit UI rendering functions
"""

import streamlit as st
import pandas as pd
from typing import Dict, Tuple

from data_service.data_processor import DataProcessor, CustomRateBuilder, DataFilterer
from utils.chart_generator import ChartGenerator
from utils.pdf_generator import generate_pdf_from_df
from constants.fred import FRED_SERIES_REGISTRY
from views.fred_ui import FredRatesUI
from views.fhlb_ui import FHLBRatesUI
from views.farmer_mac_ui import FarmerMacRatesUI


class CustomRateBuilderUI:
    """UI components for custom rate builder section"""
    
    def __init__(self, data_processor: DataProcessor, chart_generator: ChartGenerator):
        self.data_processor = data_processor
        self.chart_generator = chart_generator
        self.rate_builder = CustomRateBuilder(data_processor)
        self.filterer = DataFilterer()
    
    def render(self):
        """Render complete custom rate builder section"""
        st.subheader("📐 Custom Rate Builder")
        
        mode = st.radio("Select mode", ["Simple", "Advanced"], horizontal=True)
        
        if mode == "Simple":
            self._render_simple_mode()
        else:
            self._render_advanced_mode()
    
    def _render_simple_mode(self):
        """Render simple custom rate builder"""
        selected_base = st.selectbox("Choose base rate", list(FRED_SERIES_REGISTRY.keys()))
        operation = st.selectbox("Select operation", ["Add", "Subtract", "Multiply", "Divide"])
        custom_value = st.number_input("Enter custom numeric adjustment", value=0.0)
        
        custom_series, rate_name = self.rate_builder.create_simple_custom_rate(
            selected_base, operation, custom_value
        )
        
        if custom_series.empty:
            st.warning("No data available for selected rate.")
            return
        
        st.markdown(f"Creating: **Custom Rate = {rate_name}**")
        
        if st.button("💾 Save Custom Rate"):
            self.rate_builder.save_custom_rate(rate_name, custom_series)
            st.success(f"Saved: {rate_name}")
        
        self._render_custom_rate_analysis(custom_series, rate_name)
    
    def _render_advanced_mode(self):
        """Render advanced custom rate builder"""
        num_components = st.number_input("How many rates to combine?", min_value=1, max_value=5, step=1, value=2)
        
        components = []
        for i in range(num_components):
            col = st.selectbox(f"Select Rate {i+1}", list(FRED_SERIES_REGISTRY.keys()), key=f"rate_{i}")
            weight = st.number_input(f"Weight for {col} (%)", key=f"weight_{i}", value=50.0)
            components.append((col, weight))
        
        custom_series, rate_name = self.rate_builder.create_weighted_custom_rate(components)
        
        if custom_series.empty:
            st.warning("One or more selected series have no data.")
            return
        
        st.markdown(f"**Formula:** {rate_name}")
        
        if st.button("💾 Save Custom Rate"):
            self.rate_builder.save_custom_rate(rate_name, custom_series)
            st.success(f"Saved: {rate_name}")
        
        self._render_custom_rate_analysis(custom_series, rate_name)
    
    def _render_custom_rate_analysis(self, custom_series: pd.Series, rate_name: str):
        """Render custom rate chart and analysis tools"""
        # Chart with download
        fig = self.chart_generator.create_custom_rate_chart(custom_series, rate_name)
        st.pyplot(fig)
        
        buf = self.chart_generator.save_chart_to_buffer(fig)
        st.download_button(
            label="📥 Download Chart as PNG",
            data=buf.getvalue(),
            file_name=f"{rate_name} Over Time.png",
            mime="image/png"
        )
        
        # Date analysis tabs
        tab1, tab2 = st.tabs(["🔘 Specific Date", "📆 Date Range"])
        
        with tab1:
            self._render_custom_specific_date(custom_series)
        
        with tab2:
            self._render_custom_date_range(custom_series, rate_name)
    
    def _render_custom_specific_date(self, custom_series: pd.Series):
        """Render specific date lookup for custom rates"""
        date_val = st.date_input(
            "Select Date", value=custom_series.index.max().date(),
            min_value=custom_series.index.min().date(),
            max_value=custom_series.index.max().date(),
            key="custom_date"
        )
        selected = custom_series[custom_series.index.date == date_val]
        if not selected.empty:
            st.subheader(f"Custom Rate on {date_val}")
            st.write(selected.iloc[0])
        else:
            st.warning("No data for the selected date.")
    
    def _render_custom_date_range(self, custom_series: pd.Series, rate_name: str):
        """Render date range analysis for custom rates"""
        date_range = st.date_input(
            "Select Date Range",
            value=(custom_series.index.min().date(), custom_series.index.max().date()),
            min_value=custom_series.index.min().date(),
            max_value=custom_series.index.max().date(),
            key="custom_range"
        )
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            if start_date > end_date:
                st.error("Start date must be before end date.")
                return
            
            range_df = custom_series[
                (custom_series.index.date >= start_date) & 
                (custom_series.index.date <= end_date)
            ]
            
            if not range_df.empty:
                st.subheader(f"Custom Rate from {start_date} to {end_date}")
                
                # Range chart
                fig = self.chart_generator.create_custom_rate_chart(range_df, rate_name)
                st.pyplot(fig)
                
                buf = self.chart_generator.save_chart_to_buffer(fig)
                st.download_button(
                    label="📥 Download Chart as PNG",
                    data=buf.getvalue(),
                    file_name=f"{rate_name} from {start_date} to {end_date}.png",
                    mime="image/png",
                    key="custom_range_chart"
                )
                
                # Data table
                st.subheader("Custom Rate Table")
                named_df = range_df.rename("Custom Rate").to_frame().reset_index()
                named_df.columns = ["Date", "Custom Rate"]
                named_df["Date"] = named_df["Date"].dt.strftime("%Y-%m")
                st.dataframe(named_df)
                
                pdf_buf = generate_pdf_from_df(named_df, title="Custom Rate Table")
                st.download_button(
                    label="📄 Download Custom Rate Dataset As a PDF",
                    data=pdf_buf,
                    file_name=f"{rate_name} Table.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("No data for selected range.")
        else:
            st.info("Please select both start and end dates.")



class NavigationUI:
    """UI components for app navigation and layout"""
    
    @staticmethod
    def render_header():
        """Render app header and title"""
        st.image("public/Logo dark.png", width=200)
        st.title("📈 Banking Rates Dashboard")
        st.write("Fetching data directly from the U.S. Treasury and FRED.")
    
    @staticmethod
    def render_section_selector() -> str:
        """Render section selection dropdown"""
        return st.selectbox(
            "Select Dataset", [
                "FRED Rates", 
                "Custom Rate Builder",
                "FHLB Rates", 
                "Farmer Mac Rates",
                "📚 Financial Glossary"
            ]
        )
    
    @staticmethod
    def render_footer():
        """Render app footer"""
        st.markdown(
            "<hr><p style='text-align: center;'>Made with ❤️ by Aurore Team — "
            "<a href='https://aurorelabs.ai'>aurorelabs.ai</a></p>", 
            unsafe_allow_html=True
        )


class AppStateManager:
    """Manages application state and session variables"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        if 'custom_rates' not in st.session_state:
            st.session_state.custom_rates = {}
        
        if 'selected_choice' not in st.session_state:
            st.session_state.selected_choice = list(FRED_SERIES_REGISTRY.keys())[0]
    
    @staticmethod
    def update_selected_choice(choice: str):
        """Update selected choice in session state"""
        st.session_state.selected_choice = choice
    
    @staticmethod
    def get_custom_rates() -> Dict:
        """Get custom rates from session state"""
        return st.session_state.get('custom_rates', {})
    
    @staticmethod
    def clear_custom_rates():
        """Clear all custom rates from session state"""
        st.session_state.custom_rates = {}


class UIComponentFactory:
    """Factory class for creating UI components"""
    
    def __init__(self, data_processor: DataProcessor):
        self.data_processor = data_processor
        self.chart_generator = ChartGenerator()
    
    def create_fred_rates_ui(self) -> FredRatesUI:
        """Create FRED rates UI component"""
        return FredRatesUI(self.data_processor, self.chart_generator)
    
    def create_custom_rate_builder_ui(self) -> CustomRateBuilderUI:
        """Create custom rate builder UI component"""
        return CustomRateBuilderUI(self.data_processor, self.chart_generator)
    
    def create_fhlb_rates_ui(self) -> FHLBRatesUI:
        """Create FHLB rates UI component"""
        return FHLBRatesUI(self.data_processor, self.chart_generator)
    
    def create_farmer_mac_rates_ui(self) -> FarmerMacRatesUI:
        """Create Farmer Mac rates UI component"""
        return FarmerMacRatesUI(self.data_processor, self.chart_generator)