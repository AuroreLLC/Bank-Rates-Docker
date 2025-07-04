import streamlit as st
import pandas as pd
from data_service.data_processor import DataProcessor,  CofiDataProcessor
from utils.chart_generator import ChartGenerator
from utils.pdf_generator import generate_pdf_from_df
from views.glossary import  add_section_glossary, create_term_tooltip


class FarmerMacRatesUI:
    """UI components for Farmer Mac COFI rates section"""
    
    def __init__(self, data_processor: DataProcessor, chart_generator: ChartGenerator):
        self.data_processor = data_processor
        self.chart_generator = chart_generator
        self.cofi_processor = CofiDataProcessor()
    
    def render(self):
        """Render complete Farmer Mac rates section"""
        data, timestamp = self.data_processor.load_farm_mac_data()
        cofi_yearly = pd.DataFrame(data['yearly_resets'])
        cofi_3_months = data['monthly_3month_cofi']
        
        st.caption(f"Data fetched at: {timestamp}")
        add_section_glossary("Farmer Mac Rates")
        st.markdown(f"""
        The {create_term_tooltip("COFI", "COFI")} is a weighted-average interest rate index 
        primarily used for adjustable-rate mortgages.
        """, unsafe_allow_html=True)
        
        self._render_yearly_cofi_section(cofi_yearly)
        self._render_monthly_cofi_section(cofi_3_months)
    
    def _render_yearly_cofi_section(self, cofi_yearly: pd.DataFrame):
        """Render yearly COFI rates section"""
        st.subheader("📊 COFI Yearly Rates Overview")
        st.write("This table shows the yearly COFI rates for 1-Year, 5-Year, 10-Year, and 15-Year resets.")
        
        st.dataframe(cofi_yearly)
        
        # PDF download
        pdf_buf = generate_pdf_from_df(cofi_yearly, title="COFI Rates Summary")
        st.download_button(
            label="📄 Download Summary as PDF",
            data=pdf_buf,
            file_name="cofi_yearly_rates_summary.pdf",
            mime="application/pdf"
        )
        
        # Chart
        st.subheader("📈 COFI Yearly Rates Chart")
        df_long = self.cofi_processor.process_yearly_cofi(cofi_yearly)
        chart = self.chart_generator.create_cofi_yearly_chart(df_long)
        st.altair_chart(chart, use_container_width=True)
    
    def _render_monthly_cofi_section(self, cofi_3_months: pd.DataFrame):
        """Render monthly COFI rates section"""
        st.subheader("📈 COFI Monthly Rates Overview")
        st.write("This table shows the monthly COFI rates for 3-Month COFI.")
        st.dataframe(cofi_3_months)
        
        # PDF download
        pdf_buf = generate_pdf_from_df(cofi_3_months, title="COFI Rates Summary")
        st.download_button(
            label="📄 Download Summary as PDF",
            data=pdf_buf,
            file_name="cofi_monthly_rates_summary.pdf",
            mime="application/pdf"
        )
        
        # Chart
        st.subheader("📈 COFI monthly 3 months Rates Chart")
        processed_cofi = self.cofi_processor.process_monthly_cofi(cofi_3_months)
        chart = self.chart_generator.create_cofi_monthly_chart(processed_cofi)
        st.altair_chart(chart, use_container_width=True)
