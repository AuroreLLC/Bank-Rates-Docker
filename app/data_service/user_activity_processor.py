import pandas as pd
from datetime import datetime, date
from io import StringIO
from typing import Dict, List, Tuple, Optional

class UserActivityAnalytics:
    """Data processing class for user activity analytics"""
    
    def __init__(self, raw_logs: str):
        """Initialize with raw log data"""
        self.raw_logs = raw_logs
        self.df = None
        self._process_logs()
    
    def _process_logs(self) -> None:
        """Process raw logs into DataFrame"""
        if not self.raw_logs or self.raw_logs.strip() == "":
            self.df = pd.DataFrame()
            return
            
        try:
            self.df = pd.read_csv(StringIO(self.raw_logs))
            if not self.df.empty:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                self.df['date'] = self.df['timestamp'].dt.date
        except Exception as e:
            print(f"Error processing logs: {e}")
            self.df = pd.DataFrame()
    
    def is_data_available(self) -> bool:
        """Check if data is available for processing"""
        return not self.df.empty
    
    def get_date_range(self) -> Tuple[Optional[date], Optional[date]]:
        """Get the date range of available data"""
        if self.df.empty:
            return None, None
        return self.df['date'].min(), self.df['date'].max()
    
    def filter_by_date_range(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Filter data by date range and login events only"""
        if self.df.empty:
            return pd.DataFrame()
        
        filtered = self.df[
            (self.df['date'] >= start_date) & 
            (self.df['date'] <= end_date) &
            (self.df['event'] == 'login')
        ]
        return filtered
    
    def get_user_summary(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """Generate user login summary statistics"""
        if filtered_df.empty:
            return pd.DataFrame()
        
        summary = filtered_df.groupby('username').agg({
            'timestamp': 'count',
            'date': ['min', 'max']
        }).round(2)
        
        summary.columns = ['Total Logins', 'First Login Date', 'Last Login Date']
        summary = summary.reset_index()
        summary = summary.sort_values('Total Logins', ascending=False)
        
        return summary
    
    def get_summary_metrics(self, filtered_df: pd.DataFrame, user_summary: pd.DataFrame) -> Dict:
        """Calculate key metrics for the dashboard"""
        if filtered_df.empty or user_summary.empty:
            return {
                'total_users': 0,
                'total_logins': 0,
                'avg_logins_per_user': 0,
                'most_active_user': 'N/A'
            }
        
        total_users = len(user_summary)
        total_logins = len(filtered_df)
        avg_logins = total_logins / total_users if total_users > 0 else 0
        most_active_user = user_summary.iloc[0]['username'] if not user_summary.empty else 'N/A'
        
        return {
            'total_users': total_users,
            'total_logins': total_logins,
            'avg_logins_per_user': avg_logins,
            'most_active_user': most_active_user
        }
    
    def search_users(self, user_summary: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Filter user summary by search term"""
        if user_summary.empty or not search_term:
            return user_summary
        
        return user_summary[
            user_summary['username'].str.contains(search_term, case=False, na=False)
        ]
    
    def get_daily_activity(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """Get daily login activity data"""
        if filtered_df.empty:
            return pd.DataFrame()
        
        daily_activity = filtered_df.groupby('date').size().reset_index(name='login_count')
        return daily_activity
    
    def get_heatmap_data(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """Get data for user activity heatmap"""
        if filtered_df.empty:
            return pd.DataFrame()
        
        heatmap_data = filtered_df.pivot_table(
            index='username',
            columns='date',
            values='timestamp',
            aggfunc='count',
            fill_value=0
        )
        return heatmap_data
    
    def export_summary_csv(self, user_summary: pd.DataFrame) -> str:
        """Export user summary as CSV string"""
        return user_summary.to_csv(index=False)
    
    def export_filtered_logs_csv(self, filtered_df: pd.DataFrame) -> str:
        """Export filtered logs as CSV string"""
        return filtered_df.to_csv(index=False)
