"""
Enhanced session state manager for Banking Rates Dashboard
Handles all session state initialization to prevent attribute errors
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
from constants.defaults import DEFAULT_SESSION_STATE


class SessionStateManager:
    """Session state manager with comprehensive initialization"""
    DEFAULT_SESSION_STATE = DEFAULT_SESSION_STATE

    @classmethod
    def initialize_all_session_state(cls):
        """Initialize all session state variables with safe defaults"""
        for key, default_value in cls.DEFAULT_SESSION_STATE.items():
            if key not in st.session_state:
                if isinstance(default_value, (dict, list)):
                    import copy
                    st.session_state[key] = copy.deepcopy(default_value)
                else:
                    st.session_state[key] = default_value
    
    @classmethod
    def safe_get(cls, key: str, default: Any = None) -> Any:
        """Safely get a session state value with fallback"""
        try:
            if key in st.session_state:
                return st.session_state[key]
            else:
                default_value = cls.DEFAULT_SESSION_STATE.get(key, default)
                st.session_state[key] = default_value
                return default_value
        except Exception:
            return default
    
    @classmethod
    def safe_set(cls, key: str, value: Any) -> bool:
        """Safely set a session state value"""
        try:
            st.session_state[key] = value
            return True
        except Exception:
            return False
    
    @classmethod
    def reset_section(cls, section: str):
        """Reset session state for a specific section"""
        section_keys = {
            'auth': ['authentication_status', 'username', 'name', 'login_processed'],
            'data': ['custom_rates', 'selected_choice', 'data_refresh_needed'],
            'ui': ['show_advanced_options', 'chart_preferences', 'sidebar_state'],
            'errors': ['last_error', 'error_count', 'error_history']
        }
        
        if section in section_keys:
            for key in section_keys[section]:
                if key in cls.DEFAULT_SESSION_STATE:
                    cls.safe_set(key, cls.DEFAULT_SESSION_STATE[key])
    
    @classmethod
    def add_notification(cls, message: str, type: str = 'info'):
        """Add a notification to the session state"""
        notifications = cls.safe_get('notifications', [])
        notification = {
            'message': message,
            'type': type,
            'timestamp': datetime.now(),
            'id': len(notifications)
        }
        notifications.append(notification)
        cls.safe_set('notifications', notifications)
    
    @classmethod
    def clear_notifications(cls):
        """Clear all notifications"""
        cls.safe_set('notifications', [])
    
    @classmethod
    def increment_counter(cls, counter_name: str) -> int:
        """Safely increment a counter"""
        current_value = cls.safe_get(counter_name, 0)
        new_value = current_value + 1
        cls.safe_set(counter_name, new_value)
        return new_value
    
    @classmethod
    def add_to_list(cls, list_key: str, item: Any, max_length: Optional[int] = None):
        """Safely add item to a list in session state"""
        current_list = cls.safe_get(list_key, [])
        current_list.append(item)
        
        if max_length and len(current_list) > max_length:
            current_list = current_list[-max_length:]
        
        cls.safe_set(list_key, current_list)
    
    @classmethod
    def update_dict(cls, dict_key: str, key: str, value: Any):
        """Safely update a dictionary in session state"""
        current_dict = cls.safe_get(dict_key, {})
        current_dict[key] = value
        cls.safe_set(dict_key, current_dict)
    
    @classmethod
    def get_session_info(cls) -> Dict[str, Any]:
        """Get information about current session state"""
        return {
            'initialized_keys': len([k for k in cls.DEFAULT_SESSION_STATE.keys() if k in st.session_state]),
            'total_keys': len(cls.DEFAULT_SESSION_STATE.keys()),
            'custom_keys': len([k for k in st.session_state.keys() if k not in cls.DEFAULT_SESSION_STATE]),
            'session_size': len(st.session_state.keys())
        }
    
    @classmethod
    def cleanup_old_data(cls, max_age_hours: int = 24):
        """Clean up old data from session state"""
        current_time = datetime.now()
        
        notifications = cls.safe_get('notifications', [])
        fresh_notifications = []
        for notif in notifications:
            if hasattr(notif, 'timestamp'):
                age = (current_time - notif['timestamp']).total_seconds() / 3600
                if age < max_age_hours:
                    fresh_notifications.append(notif)
        cls.safe_set('notifications', fresh_notifications)
        
        error_history = cls.safe_get('error_history', [])
        fresh_errors = []
        for error in error_history:
            if hasattr(error, 'timestamp'):
                age = (current_time - error['timestamp']).total_seconds() / 3600
                if age < max_age_hours:
                    fresh_errors.append(error)
        cls.safe_set('error_history', fresh_errors)


class SessionStateDecorator:
    """Decorator to ensure session state is initialized before function execution"""
    
    @staticmethod
    def ensure_initialized(func):
        """Decorator to ensure session state is initialized"""
        def wrapper(*args, **kwargs):
            SessionStateManager.initialize_all_session_state()
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def with_error_handling(func):
        """Decorator to handle session state errors gracefully"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AttributeError as e:
                if "session_state" in str(e):
                    SessionStateManager.initialize_all_session_state()
                    return func(*args, **kwargs)
                else:
                    raise e
        return wrapper


def safe_session_get(key: str, default: Any = None) -> Any:
    """Convenient function to safely get session state values"""
    return SessionStateManager.safe_get(key, default)

def safe_session_set(key: str, value: Any) -> bool:
    """Convenient function to safely set session state values"""
    return SessionStateManager.safe_set(key, value)

def ensure_session_key(key: str, default: Any = None):
    """Ensure a session state key exists"""
    if key not in st.session_state:
        st.session_state[key] = default