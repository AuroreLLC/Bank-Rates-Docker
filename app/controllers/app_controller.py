"""
Application controller module for Banking Rates Dashboard
Updated to include authentication and user management with Guest access
"""

import streamlit as st
import os
from dotenv import load_dotenv
from typing import Optional, List

from data_service.data_processor import DataProcessor
from views.ui_components import (
    UIComponentFactory, NavigationUI, AppStateManager,
    FredRatesUI, CustomRateBuilderUI, FHLBRatesUI, FarmerMacRatesUI
)
from auth.auth_manager import AuthenticationManager, UserPermissionManager, SessionStateManager
from views.auth_ui import AuthUI 
from views.glossary import render_sidebar_glossary, render_full_glossary
from lib.logger_setup import setup_logging
import traceback


class AuthenticatedBankingRatesController:
    """Main application controller with authentication and guest access"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config = self._load_configuration()
        
        self.auth_manager = AuthenticationManager(allow_guest=True)
        self.permission_manager = UserPermissionManager(self.auth_manager.config)
        
        self.auth_ui = AuthUI(self.auth_manager, self.permission_manager)
        
        SessionStateManager.initialize_auth_session()
        self._initialize_all_session_state()
        
        self.data_processor = None
        self.ui_factory = None
        
        self.logger.info("Authenticated Banking Rates Application initialized with guest access")
    
    def _setup_logging(self):
        log_config = setup_logging("Bank-Rates", "INFO")
        return log_config.get_logger("app")
    
    def _initialize_all_session_state(self):
        SessionStateManager.initialize_auth_session()
        
        if 'custom_rates' not in st.session_state:
            st.session_state.custom_rates = {}
        
        if 'selected_choice' not in st.session_state:
            st.session_state.selected_choice = None
        
        if 'favorite_terms' not in st.session_state:
            st.session_state.favorite_terms = []
        
        if 'glossary_expanded' not in st.session_state:
            st.session_state.glossary_expanded = False
        
        if 'search_term' not in st.session_state:
            st.session_state.search_term = ""
        
        if 'show_advanced_options' not in st.session_state:
            st.session_state.show_advanced_options = False
        
        if 'chart_preferences' not in st.session_state:
            st.session_state.chart_preferences = {
                'theme': 'default',
                'color_scheme': 'blue',
                'show_grid': True
            }
        
        if 'data_refresh_needed' not in st.session_state:
            st.session_state.data_refresh_needed = False
        
        if 'last_data_fetch' not in st.session_state:
            st.session_state.last_data_fetch = None
        
        if 'last_error' not in st.session_state:
            st.session_state.last_error = None
        
        if 'error_count' not in st.session_state:
            st.session_state.error_count = 0
    
    def _load_configuration(self) -> dict:
        load_dotenv()
        
        config = {
            'fred_api_key': os.getenv("FRED_API_KEY"),
            'fred_base_url': os.getenv("FRED_BASE_URL")
        }
        
        if not config['fred_api_key']:
            self.logger.warning("FRED_API_KEY not found - some features may be limited")
        if not config['fred_base_url']:
            config['fred_base_url'] = "https://api.stlouisfed.org/fred"
        
        return config
    
    def _initialize_data_components(self):
        if not self.data_processor:
            self.data_processor = DataProcessor(
                fred_api_key=self.config['fred_api_key'],
                fred_base_url=self.config['fred_base_url']
            )
            self.ui_factory = UIComponentFactory(self.data_processor)
    
    def run(self):
        try:
            self._configure_page()
            self._render_header()
            self._handle_authentication()
            
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            st.error("An error occurred while running the application.")
            
            if self.auth_manager.is_authenticated():
                if st.button("🔄 Reset Session"):
                    SessionStateManager.clear_auth_session()
                    st.rerun()
    
    def _configure_page(self):
        pass
    
    def _render_header(self):
        st.image("public/Logo dark.png", width=200)
        st.title("📈 Banking Rates Dashboard")
    
    def _handle_authentication(self):
        self.auth_manager.show_login_form()
        
        auth_status = self.auth_manager.get_authentication_status()
        
        if auth_status is True:
            self._handle_authenticated_user()
            
        elif auth_status == "guest":
            self._handle_guest_user()
            
        elif auth_status is False:
            st.error("❌ Incorrect username or password")
            self.auth_manager.cleanup_session_on_failed_auth()
            
        elif auth_status is None:
            self._render_welcome_screen()
    
    def _render_welcome_screen(self):
        st.warning("Please enter your credentials or access as guest to use the Banking Rates Dashboard")
        self.auth_manager.cleanup_session_on_failed_auth()
        
        self.auth_ui._render_public_info()
        
        st.markdown("---")
        st.markdown("### 🚪 Guest Access")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ **As a guest you can:**")
            st.markdown("""
            - View basic bank rate data
            - Browse main charts
            - Consult the financial glossary
            - Explore FRED and FHLB rates
            """)
        
        with col2:
            st.markdown("#### ❌ **Guest access limitations:**")
            st.markdown("""
            - Cannot download data
            - Cannot create custom rates
            - No access to admin features
            - Cannot view detailed histories
            """)
        
        st.info("💡 **Tip:** Register for full access to all advanced features")
    
    def _handle_guest_user(self):
        self.auth_manager.process_login()
        self._initialize_data_components()
        self.auth_manager.render_user_info_sidebar()
        st.info("🚶 **Browsing as guest** - Limited functionality available")
        
        with st.expander("🔐 Want more features?"):
            st.markdown("""
            **Register to get:**
            - ✅ Data downloads in multiple formats
            - ✅ Custom rate builder
            - ✅ Detailed activity histories
            - ✅ Admin features (based on role)
            - ✅ Priority technical support
            """)
            st.info("Contact the administrator to get a full account")
        
        self._render_guest_content()
    
    def _handle_authenticated_user(self):
        self.auth_manager.process_login()
        self._initialize_data_components()
        self.auth_manager.render_user_info_sidebar()
        self._render_authenticated_content()
        
        username = self.auth_manager.get_current_user()
        if self.permission_manager.has_permission(username, 'view_logs'):
            self.auth_manager.show_logs_expander()
    
    def _render_guest_content(self):
        st.success('🚶 Welcome, Guest! Explore the basic features of the dashboard.')
        st.write("Viewing data directly from the U.S. Treasury and FRED (limited features).")
        available_sections = self._get_guest_sections()
        render_sidebar_glossary()
        selected_section = st.selectbox("Select Dataset (Limited Access)", available_sections)
        self._route_to_guest_section(selected_section)
        NavigationUI.render_footer()
    
    def _render_authenticated_content(self):
        user_name = self.auth_manager.get_current_user_name()
        st.success(f'Welcome, {user_name}!')
        st.write("Fetching data directly from the U.S. Treasury and FRED.")
        username = self.auth_manager.get_current_user()
        available_sections = self._get_available_sections(username)
        render_sidebar_glossary()
        selected_section = st.selectbox("Select Dataset", available_sections)
        self._route_to_section(selected_section)
        NavigationUI.render_footer()
    
    def _get_guest_sections(self) -> List[str]:
        return [
            "FRED Rates (Limited View)",
            "FHLB Rates (Limited View)", 
            "📚 Financial Glossary"
        ]
    
    def _get_available_sections(self, username: str) -> List[str]:
        base_sections = [
            "FRED Rates",
            "FHLB Rates", 
            "Farmer Mac Rates",
            "📚 Financial Glossary"
        ]
        
        if self.permission_manager.has_permission(username, 'create_custom_rates'):
            base_sections.insert(1, "Custom Rate Builder")
        
        if self.permission_manager.has_permission(username, 'manage_users'):
            base_sections.append("📊 Admin Dashboard")
        
        return base_sections
    
    def _route_to_guest_section(self, section: str):
        guest_handlers = {
            "FRED Rates (Limited View)": self._handle_guest_fred_rates,
            "FHLB Rates (Limited View)": self._handle_guest_fhlb_rates,
            "📚 Financial Glossary": self._handle_glossary
        }
        
        handler = guest_handlers.get(section)
        if handler:
            try:
                handler()
            except Exception as e:
                traceback.print_exc()
                self.logger.error(f"Error in guest section '{section}': {str(e)}")
                st.error(f"An error occurred while loading the {section} section.")
        else:
            st.error(f"Unknown section: {section}")
    
    def _route_to_section(self, section: str):
        username = self.auth_manager.get_current_user()
        
        section_handlers = {
            "FRED Rates": self._handle_fred_rates,
            "Custom Rate Builder": self._handle_custom_rate_builder,
            "FHLB Rates": self._handle_fhlb_rates,
            "Farmer Mac Rates": self._handle_farmer_mac_rates,
            "📚 Financial Glossary": self._handle_glossary,
            "📊 Admin Dashboard": self._handle_admin_dashboard
        }
        
        handler = section_handlers.get(section)
        if handler:
            try:
                if section == "Custom Rate Builder" and not self.permission_manager.has_permission(username, 'create_custom_rates'):
                    st.warning("You don't have permission to access the Custom Rate Builder.")
                    return
                
                if section == "📊 Admin Dashboard" and not self.permission_manager.has_permission(username, 'manage_users'):
                    st.warning("You don't have admin permissions.")
                    return
                
                handler()
                
            except Exception as e:
                traceback.print_exc()
                self.logger.error(f"Error in section '{section}': {str(e)}")
                st.error(f"An error occurred while loading the {section} section.")
        else:
            st.error(f"Unknown section: {section}")
    
    def _handle_guest_fred_rates(self):
        self.logger.info("Rendering FRED rates section for guest")
        
        st.subheader("📊 FRED Rates - Limited View")
        st.info("🚶 **Guest Mode:** Basic visualization available. Register for full features.")
        
        fred_ui = self.ui_factory.create_fred_rates_ui()
        original_render = fred_ui.render
        
        def guest_render():
            original_render()
            st.warning("⚠️ **Guest Limitations:**")
            st.markdown("""
            - Data download is not available
            - Limited view of time series
            - Cannot customize advanced parameters
            """)
            if st.button("🔐 Upgrade for full access"):
                st.info("Contact the administrator to get a full account")
        
        fred_ui.render = guest_render
        fred_ui.render()
    
    def _handle_guest_fhlb_rates(self):
        self.logger.info("Rendering FHLB rates section for guest")
        
        st.subheader("🏦 FHLB Rates - Limited View")
        st.info("🚶 **Guest Mode:** Basic visualization available. Register for full features.")
        
        fhlb_ui = self.ui_factory.create_fhlb_rates_ui()
        original_render = fhlb_ui.render
        
        def guest_render():
            original_render()
            st.warning("⚠️ **Guest Limitations:**")
            st.markdown("""
            - Data download is not available
            - Limited view of historical rates
            - Cannot generate custom reports
            """)
            if st.button("🔐 Upgrade for full access", key="fhlb_upgrade"):
                st.info("Contact the administrator to get a full account")
        
        fhlb_ui.render = guest_render
        fhlb_ui.render()
    
    def _handle_fred_rates(self):
        self.logger.info("Rendering FRED rates section")
        fred_ui = self.ui_factory.create_fred_rates_ui()
        fred_ui.render()
    
    def _handle_custom_rate_builder(self):
        self.logger.info("Rendering custom rate builder section")
        custom_ui = self.ui_factory.create_custom_rate_builder_ui()
        custom_ui.render()
    
    def _handle_fhlb_rates(self):
        self.logger.info("Rendering FHLB rates section")
        fhlb_ui = self.ui_factory.create_fhlb_rates_ui()
        fhlb_ui.render()
    
    def _handle_farmer_mac_rates(self):
        self.logger.info("Rendering Farmer Mac rates section")
        farmer_ui = self.ui_factory.create_farmer_mac_rates_ui()
        farmer_ui.render()
    
    def _handle_glossary(self):
        self.logger.info("Rendering glossary section")
        render_full_glossary()
    
    def _handle_admin_dashboard(self):
        self.logger.info("Rendering admin dashboard")
        
        if self.auth_manager.is_guest():
            st.error("🚫 Guests cannot access the admin dashboard")
            st.info("Register to get access to administrative features")
            return
        
        try:
            username = self.auth_manager.get_current_user()
            if not self.permission_manager.has_permission(username, 'manage_users'):
                st.warning("You don't have admin permissions.")
                return
            
            if not hasattr(self.auth_ui, 'logger'):
                self.auth_ui.logger = self.logger
            
            self.auth_ui.render_admin_dashboard()
            self.auth_ui.render_permissions()
            
        except Exception as e:
            self.logger.error(f"Error rendering admin dashboard: {str(e)}")
            st.error("An error occurred while loading the admin dashboard.")
            st.subheader("📊 Basic Admin Dashboard")
            st.info("Advanced features are temporarily unavailable. Showing basic admin info.")
            self._render_basic_admin_dashboard()
    
    def _render_basic_admin_dashboard(self):
        st.subheader("📊 Basic Admin Dashboard")
        st.subheader("📜 User Activity Logs")
        logs = self.auth_manager.get_user_logs()
        st.text_area("All User Activity", logs, height=300)
        st.download_button(
            label="📥 Download Activity Logs",
            data=logs,
            file_name=f"user_activity_{st.session_state.get('username', 'admin')}.csv",
            mime="text/csv"
        )
        st.subheader("🔧 Session Management")
        if st.button("🔄 Reset All Sessions"):
            SessionStateManager.reset_session()
            st.success("All sessions have been reset.")
            st.rerun()
        st.subheader("👥 User Permissions")
        current_user = self.auth_manager.get_current_user()
        user_role = self.permission_manager.get_user_role(current_user)
        st.info(f"Your role: **{user_role}**")
        permissions = [
            'view_data', 'download_data', 'create_custom_rates', 
            'view_logs', 'manage_users'
        ]
        st.write("**Your permissions:**")
        for perm in permissions:
            has_perm = self.permission_manager.has_permission(current_user, perm)
            emoji = "✅" if has_perm else "❌"
            st.write(f"{emoji} {perm.replace('_', ' ').title()}")


"""
INTEGRATION STEPS FOR GUEST ACCESS:

1. Update your AuthenticationManager in auth/auth_manager.py with the guest functionality

2. Make sure your UserPermissionManager handles the 'guest' role properly

3. Update your UI components to handle guest restrictions:
   - Remove or disable download buttons for guests
   - Show upgrade prompts where appropriate
   - Limit data visualization complexity for guests

4. Update your config.yaml to include any guest-specific settings if needed

5. Test the guest flow:
   - Guest login works
   - Guest users see limited functionality
   - Guest users can't access restricted features
   - Guest users see appropriate upgrade prompts

6. Optional: Add analytics to track guest user behavior for conversion optimization
"""
