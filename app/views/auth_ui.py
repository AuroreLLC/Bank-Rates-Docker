import streamlit as st
import pandas as pd
from datetime import date
from data_service.data_processor import DataProcessor, CofiDataProcessor
from data_service.user_activity_processor import UserActivityAnalytics
from utils.chart_generator import ChartGenerator
from auth.session_manager import SessionStateManager
from constants.auth import permissions
from typing import Dict

class AuthUI:
    def __init__(self, auth_manager, permission_manager):
        self.auth_manager = auth_manager
        self.permission_manager = permission_manager
    
    def render_admin_dashboard(self):
        """Render admin dashboard with enhanced functionality"""
        st.subheader("📊 Admin Dashboard")
        tab1, tab2, tab3 = st.tabs(["Activity Summary", "Raw Logs", "Session Management"])
        with tab1:
            self.render_user_activity_summary()
        with tab2:
            self._render_raw_logs()
        with tab3:
            self._render_session_management()
    
    def _render_raw_logs(self):
        """Render raw logs section"""
        st.subheader("📜 User Activity Logs")
        logs = self.auth_manager.get_user_logs()
        st.text_area("All User Activity", logs, height=300)
        st.download_button(
            label="📥 Download Activity Logs",
            data=logs,
            file_name=f"user_activity_{st.session_state.get('username', 'admin')}.csv",
            mime="text/csv"
        )
    
    def _render_session_management(self):
        """Render session management section"""
        st.subheader("🔧 Session Management")
        if st.button("🔄 Reset All Sessions"):
            SessionStateManager.reset_session()
            st.success("All sessions have been reset.")
            st.rerun()
    
    def render_permissions(self):
        """Render user permissions section"""
        st.subheader("👥 User Permissions")
        current_user = self.auth_manager.get_current_user()
        user_role = self.permission_manager.get_user_role(current_user)
        st.info(f"Your role: **{user_role}**")
        st.write("**Your permissions:**")
        for perm in permissions:
            has_perm = self.permission_manager.has_permission(current_user, perm)
            emoji = "✅" if has_perm else "❌"
            st.write(f"{emoji} {perm.replace('_', ' ').title()}")
    
    def render_user_activity_summary(self):
        """Render user activity summary with date filtering using Altair charts"""
        st.subheader("👥 User Activity Summary")
        logs = self.auth_manager.get_user_logs()
        analytics = UserActivityAnalytics(logs)
        if not analytics.is_data_available():
            st.warning("No activity logs available.")
            return
        self._render_date_filters(analytics)
        start_date = st.session_state.get('activity_start_date')
        end_date = st.session_state.get('activity_end_date')
        if not start_date or not end_date:
            return
        filtered_df = analytics.filter_by_date_range(start_date, end_date)
        if filtered_df.empty:
            st.warning("No login data found for the selected date range.")
            return
        user_summary = analytics.get_user_summary(filtered_df)
        metrics = analytics.get_summary_metrics(filtered_df, user_summary)
        self._render_metrics(metrics)
        self._render_user_summary_table(analytics, user_summary)
        self._render_visualizations(analytics, filtered_df, user_summary)
        self._render_export_section(analytics, user_summary, filtered_df, start_date, end_date)
    
    def _render_date_filters(self, analytics: UserActivityAnalytics):
        """Render date filter controls"""
        st.subheader("📅 Date Filter")
        min_date, max_date = analytics.get_date_range()
        if not min_date or not max_date:
            return
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key='activity_start_date'
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key='activity_end_date'
            )
    
    def _render_metrics(self, metrics: Dict):
        """Render key metrics cards"""
        st.subheader("📊 Activity Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", metrics['total_users'])
        with col2:
            st.metric("Total Logins", metrics['total_logins'])
        with col3:
            st.metric("Avg Logins per User", f"{metrics['avg_logins_per_user']:.1f}")
        with col4:
            st.metric("Most Active User", metrics['most_active_user'])
    
    def _render_user_summary_table(self, analytics: UserActivityAnalytics, user_summary: pd.DataFrame):
        """Render user summary table with search"""
        st.subheader("👤 User Login Summary")
        search_user = st.text_input("🔍 Search User", placeholder="Enter username to filter...")
        display_summary = analytics.search_users(user_summary, search_user)
        if not display_summary.empty:
            st.dataframe(
                display_summary,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "username": st.column_config.TextColumn("Username", width="medium"),
                    "Total Logins": st.column_config.NumberColumn("Total Logins", format="%d"),
                    "First Login Date": st.column_config.DateColumn("First Login"),
                    "Last Login Date": st.column_config.DateColumn("Last Login")
                }
            )
        else:
            st.info("No users found matching your search criteria.")
    
    def _render_visualizations(self, analytics: UserActivityAnalytics, filtered_df: pd.DataFrame, 
                              user_summary: pd.DataFrame):
        """Render data visualizations using Altair charts"""
        st.subheader("📈 Activity Visualizations")
        viz_tab1, viz_tab2, viz_tab3, viz_tab4, viz_tab5 = st.tabs([
            "📊 User Rankings", 
            "📈 Daily Trend", 
            "🗓️ Activity Heatmap", 
            "🥧 Distribution", 
            "📉 Frequency"
        ])
        with viz_tab1:
            self._render_user_login_chart(user_summary)
        with viz_tab2:
            self._render_daily_activity_chart(analytics, filtered_df)
        with viz_tab3:
            self._render_activity_heatmap(analytics, filtered_df)
        with viz_tab4:
            self._render_distribution_chart(user_summary)
        with viz_tab5:
            self._render_frequency_histogram(user_summary)
    
    def _render_user_login_chart(self, user_summary: pd.DataFrame):
        """Render user login count chart using Altair"""
        if user_summary.empty:
            st.info("No data available for user rankings.")
            return
        try:
            chart = ChartGenerator.create_user_login_bar_chart(user_summary, top_n=10)
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering user login chart: {str(e)}")
    
    def _render_daily_activity_chart(self, analytics: UserActivityAnalytics, filtered_df: pd.DataFrame):
        """Render daily activity chart using Altair"""
        daily_activity = analytics.get_daily_activity(filtered_df)
        if daily_activity.empty:
            st.info("No data available for daily activity.")
            return
        try:
            chart = ChartGenerator.create_daily_activity_line_chart(daily_activity)
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering daily activity chart: {str(e)}")
    
    def _render_activity_heatmap(self, analytics: UserActivityAnalytics, filtered_df: pd.DataFrame):
        """Render user activity heatmap using Altair"""
        heatmap_data = analytics.get_heatmap_data(filtered_df)
        if heatmap_data.empty:
            st.info("No data available for activity heatmap.")
            return
        try:
            chart = ChartGenerator.create_activity_heatmap(heatmap_data)
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering activity heatmap: {str(e)}")
    
    def _render_distribution_chart(self, user_summary: pd.DataFrame):
        """Render user activity distribution chart using Altair"""
        if user_summary.empty:
            st.info("No data available for distribution chart.")
            return
        try:
            chart = ChartGenerator.create_user_activity_pie_chart(user_summary, top_n=8)
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering distribution chart: {str(e)}")
    
    def _render_frequency_histogram(self, user_summary: pd.DataFrame):
        """Render login frequency histogram using Altair"""
        if user_summary.empty:
            st.info("No data available for frequency distribution.")
            return
        try:
            chart = ChartGenerator.create_login_frequency_histogram(user_summary)
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering frequency histogram: {str(e)}")
    
    def _render_export_section(self, analytics: UserActivityAnalytics, user_summary: pd.DataFrame, 
                              filtered_df: pd.DataFrame, start_date: date, end_date: date):
        """Render data export section"""
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        with col1:
            summary_csv = analytics.export_summary_csv(user_summary)
            st.download_button(
                label="📥 Download Summary CSV",
                data=summary_csv,
                file_name=f"user_activity_summary_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
        with col2:
            filtered_csv = analytics.export_filtered_logs_csv(filtered_df)
            st.download_button(
                label="📥 Download Filtered Logs CSV",
                data=filtered_csv,
                file_name=f"filtered_user_logs_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )

    def _render_public_info(self):
        """Show public information for non-authenticated users"""
        st.info("📊 **Banking Rates Dashboard** - Real-time financial data from FRED and other sources")
        with st.expander("ℹ️ About This Application"):
            st.markdown("""
            **Features:**
            - Real-time FRED rates data
            - FHLB rates monitoring
            - Farmer Mac COFI rates
            - Custom rate calculations
            - PDF exports and data downloads
            - Interactive charts and visualizations
            
            **Please log in to access all features.**
            """)
        st.markdown("---")
        st.write("🔒 **Login required to access full dashboard**")
