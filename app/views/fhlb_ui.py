import streamlit as st
import pandas as pd
from data_service.data_processor import DataProcessor
from utils.chart_generator import ChartGenerator
from utils.pdf_generator import generate_pdf_from_df

from views.glossary import  add_section_glossary, create_term_tooltip


class FHLBRatesUI:
    """UI components for FHLB rates section"""
    
    def __init__(self, data_processor: DataProcessor, chart_generator: ChartGenerator):
        self.data_processor = data_processor
        self.chart_generator = chart_generator
    
    def render(self):
        """Render complete FHLB rates section"""
        rates = self.data_processor.load_fhlb_data()
        timestamp = rates['timestamp']
        short_term_df = rates['short_term_fixed']
        long_term_df = rates['long_term_fixed']
        summary_df = pd.concat([short_term_df, long_term_df], ignore_index=True)
        
        st.caption(f"Data fetched at: {timestamp}")
        st.subheader("📊 FHLB Rates Overview")
        add_section_glossary("FHLB Rates")
        st.markdown(f"""
        The {create_term_tooltip("FHLB", "FHLB")} rates provide liquidity to financial institutions 
        for mortgage lending and community development.
        """, unsafe_allow_html=True)
        
        st.dataframe(summary_df)
        
        # PDF download
        pdf_buf = generate_pdf_from_df(summary_df, title="FHLB Rates Summary")
        st.download_button(
            label="📄 Download Summary as PDF",
            data=pdf_buf,
            file_name="FHLB_rates_summary.pdf",
            mime="application/pdf"
        )
        
        # Term selection and chart
        choice = st.selectbox("Select Term", ["Short Term", "Long Term"], index=0)
        st.subheader("📈 FHLB vs Regular Rate Chart")
        
        fhlb_df = short_term_df if choice == "Short Term" else long_term_df
        fig = self.chart_generator.create_fhlb_rate_curve(fhlb_df)
        st.pyplot(fig)
        
        # Chart download
        buf = self.chart_generator.save_chart_to_buffer(fig)
        st.download_button(
            label="📥 Download Chart as PNG",
            data=buf.getvalue(),
            file_name="FHLB_rate_curve.png",
            mime="image/png"
        )
