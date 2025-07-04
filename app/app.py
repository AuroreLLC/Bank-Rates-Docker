# main.py (Updated with Authentication)
"""
Main application entry point for Banking Rates Dashboard
Includes authentication and user management
"""

import streamlit as st
import sys
import os
from pathlib import Path

st.set_page_config(
    page_title="Banking Rates Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from controllers.app_controller import AuthenticatedBankingRatesController
    from auth.auth_manager import SessionStateManager, create_sample_config
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all required modules are available in the project directory.")
    
    with st.expander("📦 Required Dependencies"):
        st.code("""
        pip install streamlit
        pip install streamlit-authenticator
        pip install pyyaml
        pip install python-dotenv
        pip install pandas
        pip install matplotlib
        pip install altair
        """)
    
    st.stop()


def check_config_file():
    """Check if config.yaml exists and help create it if not"""
    config_path = "config.yaml"
    
    if not os.path.exists(config_path):
        st.error("🔧 Configuration file 'config.yaml' not found")
        
        with st.expander("📋 Create Configuration File"):
            st.markdown("""
            **You need to create a `config.yaml` file for authentication.**
            
            Here's a sample structure:
            """)
            
            # Show sample config
            sample_config = create_sample_config()
            import yaml
            sample_yaml = yaml.dump(sample_config, default_flow_style=False)
            st.code(sample_yaml, language='yaml')
            
            st.markdown("""
            **Steps to create your config.yaml:**
            1. Copy the above configuration
            2. Save it as `config.yaml` in your project root
            3. Update usernames, emails, and names as needed
            4. Generate hashed passwords using streamlit-authenticator
            5. Use a random string for the cookie key
            
            **To generate hashed passwords:**
            ```python
            import streamlit_authenticator as stauth
            password = "your_password"
            hashed_password = stauth.Hasher([password]).generate()[0]
            print(hashed_password)
            ```
            """)
            
            st.download_button(
                label="📥 Download Sample config.yaml",
                data=sample_yaml,
                file_name="config.yaml",
                mime="text/yaml"
            )
        
        return False
    
    return True


def check_environment():
    """Check environment variables"""
    fred_api_key = os.getenv("FRED_API_KEY")
    
    if not fred_api_key:
        st.warning("⚠️ FRED_API_KEY not found in environment")
        
        with st.expander("🔑 API Key Setup"):
            st.markdown("""
            **To get full functionality, you need a FRED API key:**
            
            1. Visit https://fred.stlouisfed.org/
            2. Create a free account
            3. Go to Account Settings > API Keys
            4. Generate a new API key
            5. Add it to your `.env` file:
            
            ```
            FRED_API_KEY=your_api_key_here
            FRED_BASE_URL=https://api.stlouisfed.org/fred
            ```
            
            **Note:** Some features will be limited without an API key.
            """)
        
        return False
    
    return True


def initialize_session():
    """Initialize session state"""
    SessionStateManager.initialize_auth_session()
    
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = False
        st.session_state.show_setup_help = False


def show_setup_help():
    """Show setup help for first-time users"""
    st.info("🚀 **Welcome to Banking Rates Dashboard!**")
    
    setup_complete = True
    
    # Check config file
    if not check_config_file():
        setup_complete = False
    
    # Check environment
    if not check_environment():
        setup_complete = False
    
    if setup_complete:
        st.success("✅ Setup complete! You can now log in to access the dashboard.")
    else:
        st.warning("⚙️ Please complete the setup steps above before proceeding.")
    
    return setup_complete


def main():
    """Main application entry point"""
    initialize_session()
    
    try:
        if not st.session_state.app_initialized:
            if not show_setup_help():
                st.stop()
        
        with st.spinner("Loading Banking Rates Dashboard..."):
            app_controller = AuthenticatedBankingRatesController()
            st.session_state.app_initialized = True
        
        app_controller.run()
        
    except FileNotFoundError as e:
        st.error("📁 Configuration Error")
        st.error(f"Required file not found: {str(e)}")
        st.info("Please check the setup instructions above.")
        
        st.session_state.app_initialized = False
        
        if st.button("🔄 Retry Setup"):
            st.rerun()
    
    except Exception as e:
        st.error("❌ Application Error")
        st.error("An unexpected error occurred.")
        
        with st.expander("🔍 Error Details"):
            st.code(str(e))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reload Application"):
                st.session_state.app_initialized = False
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Session"):
                SessionStateManager.reset_session()
                st.rerun()


if __name__ == "__main__":
    main()