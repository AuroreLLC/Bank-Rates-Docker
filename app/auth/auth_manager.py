"""
Authentication manager module for Banking Rates Dashboard
Handles user authentication, session management, and logging
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class AuthenticationManager:
    """Manages user authentication and session state"""
    
    def __init__(self, config_path: str = "config.yaml", log_file: str = "usage.log", allow_guest: bool = True):
        self.config_path = config_path
        self.log_file = log_file
        self.allow_guest = allow_guest
        self.authenticator = None
        self._setup_logging()
        self._load_config()
        self._initialize_authenticator()
    
    def _setup_logging(self):
        """Setup logging for user activities"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("timestamp,username,event,visit_count\n")
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s,%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def _load_config(self):
        """Load authentication configuration"""
        try:
            with open(self.config_path) as file:
                self.config = yaml.load(file, Loader=SafeLoader)
        except FileNotFoundError:
            st.error(f"Configuration file '{self.config_path}' not found.")
            st.info("Please create a config.yaml file with authentication settings.")
            st.stop()
        except yaml.YAMLError as e:
            st.error(f"Error parsing configuration file: {e}")
            st.stop()
    
    def _initialize_authenticator(self):
        """Initialize the Streamlit authenticator"""
        try:
            self.authenticator = stauth.Authenticate(
                self.config['credentials'],
                self.config['cookie']['name'],
                self.config['cookie']['key'],
                self.config['cookie']['expiry_days']
            )
        except KeyError as e:
            st.error(f"Missing configuration key: {e}")
            st.info("Please check your config.yaml file structure.")
            st.stop()
    
    def show_login_form(self):
        """Display the login form with guest option"""
        if self.authenticator:
            self.authenticator.login()
            if self.allow_guest and not self.is_authenticated():
                st.markdown("---")
                st.markdown("### 🚪 Guest Access")
                st.info("Access with limited functionality without credentials")
                if st.button("🔓 Enter as Guest", key="guest_login"):
                    self._login_as_guest()
    
    def _login_as_guest(self):
        """Log in as guest user"""
        st.session_state["authentication_status"] = "guest"
        st.session_state["username"] = "guest"
        st.session_state["name"] = "Guest"
        st.session_state["is_guest"] = True
        if "visit_count" not in st.session_state:
            st.session_state.visit_count = 1
        else:
            st.session_state.visit_count += 1
        logging.info(f'guest,login,{st.session_state.visit_count}')
        st.session_state['login_processed'] = True
        st.rerun()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (including guest)"""
        auth_status = st.session_state.get("authentication_status", False)
        return auth_status is True or auth_status == "guest"
    
    def is_guest(self) -> bool:
        """Check if current user is a guest"""
        return st.session_state.get("is_guest", False)
    
    def is_regular_user(self) -> bool:
        """Check if current user is a regular authenticated user (not guest)"""
        return st.session_state.get("authentication_status", False) is True
    
    def get_authentication_status(self) -> Optional[bool]:
        """Get authentication status (True, False, 'guest', or None)"""
        return st.session_state.get("authentication_status")
    
    def get_current_user(self) -> Optional[str]:
        """Get current authenticated user"""
        if self.is_authenticated():
            return st.session_state.get("username")
        return None
    
    def get_current_user_name(self) -> Optional[str]:
        """Get current authenticated user's display name"""
        if self.is_authenticated():
            return st.session_state.get("name")
        return None
    
    def process_login(self):
        """Process login and handle session management"""
        if self.is_authenticated() and 'login_processed' not in st.session_state:
            if "visit_count" not in st.session_state:
                st.session_state.visit_count = 1
            else:
                st.session_state.visit_count += 1
            username = self.get_current_user()
            visit_count = st.session_state.visit_count
            logging.info(f'{username},login,{visit_count}')
            st.session_state['login_processed'] = True
    
    def show_logout_button(self, location: str = 'sidebar'):
        """Show logout button and handle logout logic"""
        if self.is_authenticated():
            if self.is_guest():
                if location == 'sidebar':
                    with st.sidebar:
                        if st.button("🚪 Logout", key="guest_logout"):
                            self._logout_guest()
                else:
                    if st.button("🚪 Logout", key="guest_logout"):
                        self._logout_guest()
            else:
                if self.authenticator:
                    self.authenticator.logout('🚪 Log Out', location)
    
    def _logout_guest(self):
        """Handle guest logout"""
        guest_keys = ['authentication_status', 'username', 'name', 'is_guest', 
                     'login_processed', 'visit_count', 'last_login']
        for key in guest_keys:
            if key in st.session_state:
                del st.session_state[key]
        logging.info('guest,logout,0')
        st.rerun()
    
    def cleanup_session_on_failed_auth(self):
        """Clean up session state on failed authentication"""
        if 'login_processed' in st.session_state:
            del st.session_state['login_processed']
    
    def render_user_info_sidebar(self):
        """Render user information in sidebar"""
        if self.is_authenticated():
            with st.sidebar:
                user_name = self.get_current_user_name()
                user_icon = "👤" if not self.is_guest() else "🚶"
                user_type = " (Guest)" if self.is_guest() else ""
                st.write(f'{user_icon} **{user_name}**{user_type}')
                visit_count = st.session_state.get('visit_count', 0)
                st.info(f"🔁 Session visits: {visit_count}")
                if self.is_guest():
                    st.warning("⚠️ Limited access as guest")
                self.show_logout_button('sidebar')
                if 'last_login' not in st.session_state:
                    st.session_state.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"Last login: {st.session_state.last_login}")
    
    def get_user_logs(self) -> str:
        """Get user activity logs"""
        try:
            with open(self.log_file, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "No logs available"
    
    def show_logs_expander(self):
        """Show logs in an expander (only for non-guest users)"""
        if self.is_authenticated() and not self.is_guest():
            with st.expander("📜 View Activity Log"):
                logs = self.get_user_logs()
                st.text_area("Session Log", logs, height=200)


class UserPermissionManager:
    """Manages user permissions and role-based access"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def get_user_role(self, username: str) -> str:
        """Get user role from configuration"""
        if username == "guest":
            return "guest"
        try:
            user_config = self.config['credentials']['usernames'][username]
            return user_config.get('role', 'user')
        except KeyError:
            return 'user'
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        role = self.get_user_role(username)
        role_permissions = {
            'admin': ['view_data', 'download_data', 'create_custom_rates', 'view_logs', 'manage_users'],
            'power_user': ['view_data', 'download_data', 'create_custom_rates'],
            'user': ['view_data', 'download_data'],
            'guest': ['view_data','download_data']
        }
        return permission in role_permissions.get(role, [])
    
    def filter_available_sections(self, username: str, sections: list) -> list:
        """Filter available sections based on user permissions"""
        role = self.get_user_role(username)
        if role == 'guest':
            allowed_sections = ["📊 Dashboard", "📈 Rates View"]
            return [s for s in sections if s in allowed_sections]
        elif self.has_permission(username, 'view_logs'):
            return sections
        else:
            return [s for s in sections if s != "📊 Admin Dashboard"]


class SessionStateManager:
    """Manages authentication-related session state"""
    
    @staticmethod
    def initialize_auth_session():
        """Initialize authentication-related session variables"""
        auth_keys = [
            'authentication_status',
            'username', 
            'name',
            'login_processed',
            'visit_count',
            'last_login',
            'is_guest'
        ]
        for key in auth_keys:
            if key not in st.session_state:
                if key == 'visit_count':
                    st.session_state[key] = 0
                elif key == 'is_guest':
                    st.session_state[key] = False
                else:
                    st.session_state[key] = None
    
    @staticmethod
    def clear_auth_session():
        """Clear authentication session data"""
        auth_keys = [
            'authentication_status',
            'username',
            'name', 
            'login_processed',
            'visit_count',
            'last_login',
            'is_guest'
        ]
        for key in auth_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def reset_session():
        """Reset entire session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]


def create_sample_config():
    """Create a sample config.yaml file for reference"""
    sample_config = {
        'credentials': {
            'usernames': {
                'admin': {
                    'email': 'admin@example.com',
                    'name': 'Administrator',
                    'password': '$2b$12$...',
                    'role': 'admin'
                },
                'user1': {
                    'email': 'user1@example.com', 
                    'name': 'Regular User',
                    'password': '$2b$12$...',
                    'role': 'user'
                }
            }
        },
        'cookie': {
            'name': 'banking_rates_auth',
            'key': 'random_signature_key_here',
            'expiry_days': 30
        }
    }
    return sample_config
