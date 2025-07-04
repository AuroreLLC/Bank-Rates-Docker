import streamlit as st
import pandas as pd
from data_service.data_processor import DataProcessor,  DataFilterer
from utils.chart_generator import ChartGenerator
from utils.pdf_generator import generate_pdf_from_df
from constants.fred import FRED_SERIES_REGISTRY
from views.glossary import add_section_glossary, create_term_tooltip

class FredRatesUI:
    """UI components for FRED rates section"""
    
    def __init__(self, data_processor: DataProcessor, chart_generator: ChartGenerator):
        self.data_processor = data_processor
        self.chart_generator = chart_generator
        self.filterer = DataFilterer()
    
    def render(self):
        """Render complete FRED rates section"""
        st.subheader("📊 Overview of Key FRED Rates")
        add_section_glossary("FRED Rates")
        st.markdown(f"""
        This section displays the most recent rates from the {create_term_tooltip("FRED", "FRED")} system,
        including {create_term_tooltip("SOFR", "SOFR")} and other important benchmark rates.
        """, unsafe_allow_html=True)
        
        self._render_summary_table()
        self._render_series_selector()
        self._render_date_lookup()
    
    def _render_summary_table(self):
        """Render summary data table with download option"""
        summary_df, fetch_time = self.data_processor.get_combined_rate_summary()
        st.caption(f"Data fetched at: {fetch_time}")
        st.dataframe(summary_df)
        
        pdf_buf = generate_pdf_from_df(summary_df, title="FRED Summary Table")
        st.download_button(
            label="📄 Download Summary as PDF",
            data=pdf_buf,
            file_name="fred_summary.pdf",
            mime="application/pdf"
        )
    
    def _render_series_selector(self):
        """Render series selection and chart"""
        choice = st.selectbox("Select FRED Series", list(FRED_SERIES_REGISTRY.keys()))
        st.session_state['selected_choice'] = choice
        series_id = FRED_SERIES_REGISTRY[choice]['series_id']
        df = self.data_processor.load_fred_series(series_id)
        
        if df.empty:
            st.warning("No data available for selected series.")
            return
        
        st.subheader(f"{choice} Over Time")
        
        # Create and display chart
        fig = self.chart_generator.create_time_series_chart(
            df, f"{choice} Rate Over Time", choice
        )
        st.pyplot(fig)
        
        # Download button for chart
        buf = self.chart_generator.save_chart_to_buffer(fig)
        st.download_button(
            label="📥 Download Chart as PNG",
            data=buf.getvalue(),
            file_name=f"{choice.replace(' ', '_')}_rate_chart.png",
            mime="image/png"
        )
        
        return df, choice
    
    def _render_date_lookup(self):
        """Render date lookup tabs"""
        choice = st.session_state.get('selected_choice', list(FRED_SERIES_REGISTRY.keys())[0])
        print(f"The choice is: {choice}")
        series_id = FRED_SERIES_REGISTRY[choice]['series_id']
        df = self.data_processor.load_fred_series(series_id)
        
        if df.empty:
            return
        
        st.subheader("🔎 Date Lookup")
        tab1, tab2 = st.tabs(["🔘 Specific Date", "📆 Date Range"])
        
        with tab1:
            self._render_specific_date_lookup(df, choice)
        
        with tab2:
            self._render_date_range_lookup(df, choice)
    
    def _render_specific_date_lookup(self, df: pd.DataFrame, choice: str):
        """Render specific date lookup interface"""
        if "SOFR" in choice:
            date_val = st.date_input(
                "Select Date", value=df.index.max().date(),
                min_value=df.index.min().date(), max_value=df.index.max().date(),
                key="sofr_date"
            )
            selected = self.filterer.filter_by_date(df, pd.Timestamp(date_val))
        else:
            monthly = self.filterer.get_monthly_data(df)
            labels = [d.strftime('%Y-%m') for d in monthly.index]
            sel_str = st.selectbox("Select Month", labels, index=len(labels)-1, key="month_select")
            sel_date = pd.to_datetime(f"{sel_str}-01")
            selected = df.loc[df.index == sel_date]
        
        if not selected.empty:
            st.subheader(f"Rates on {selected.index.max().date()}")
            st.dataframe(selected[['value']])
        else:
            st.warning("No data available for the selected date.")
    
    def _render_date_range_lookup(self, df: pd.DataFrame, choice: str):
        """Render date range lookup interface"""
        date_range = st.date_input(
            "Select Date Range",
            value=(df.index.min().date(), df.index.max().date()),
            min_value=df.index.min().date(),
            max_value=df.index.max().date(),
            key="range_select"
        )
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            if start_date > end_date:
                st.error("Start date must be before end date.")
                return
            
            range_df = self.filterer.filter_by_date_range(
                df, pd.Timestamp(start_date), pd.Timestamp(end_date)
            )
            
            if not range_df.empty:
                st.subheader(f"Rates from {start_date} to {end_date}")
                st.dataframe(range_df[['value']])
                
                # Prepare and offer download
                named_df = self.filterer.prepare_download_data(range_df, choice)
                pdf_buf = generate_pdf_from_df(
                    named_df, title=f"{choice} from {start_date} to {end_date}"
                )
                st.download_button(
                    label="📄 Download Rates Dataset As a PDF",
                    data=pdf_buf,
                    file_name=f"{choice} from {start_date} to {end_date}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("No data found for selected range.")
        else:
            st.info("Please select both start and end dates to view data.")
