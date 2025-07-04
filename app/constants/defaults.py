
DEFAULT_SESSION_STATE = {
    # Authentication
    'authentication_status': None,
    'username': None,
    'name': None,
    'login_processed': False,
    'visit_count': 0,
    'last_login': None,
    
    # Application state
    'app_initialized': False,
    'custom_rates': {},
    'selected_choice': None,
    'current_section': 'FRED Rates',
    
    # Glossary
    'favorite_terms': [],
    'glossary_expanded': False,
    'search_term': "",
    'glossary_history': [],
    'show_definitions': True,
    
    # UI preferences
    'show_advanced_options': False,
    'chart_preferences': {
        'theme': 'default',
        'color_scheme': 'blue',
        'show_grid': True,
        'chart_type': 'line'
    },
    'sidebar_state': 'expanded',
    'dark_mode': False,
    
    # Data management
    'data_refresh_needed': False,
    'last_data_fetch': None,
    'cache_status': {},
    'data_sources_status': {},
    
    # Error handling
    'last_error': None,
    'error_count': 0,
    'error_history': [],
    'show_debug_info': False,
    
    # Form states
    'fred_date_selection': None,
    'custom_rate_name': "",
    'selected_series': [],
    'date_range_start': None,
    'date_range_end': None,
    
    # Download preferences
    'download_format': 'PDF',
    'include_charts': True,
    'chart_resolution': 'high',
    
    # Notifications
    'notifications': [],
    'show_notifications': True,
    'notification_timeout': 5,
    
    # Performance monitoring
    'page_load_time': None,
    'api_call_count': 0,
    'cache_hit_count': 0,
    'cache_miss_count': 0
}
