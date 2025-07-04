"""
Chart generation module for Banking Rates Dashboard
Handles all visualization and chart creation
"""

import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
import io
from typing import Tuple, Optional


class ChartGenerator:
    """Main chart generation class"""
    
    @staticmethod
    def create_time_series_chart(df: pd.DataFrame, title: str, 
                               rate_name: str, color: str = "steelblue") -> plt.Figure:
        """Create a time series chart for rate data"""
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.index, df['value'], label=rate_name, color=color, linewidth=2)
        ax.set_title(f"{title}", fontsize=14)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Rate (%)", fontsize=12)
        ax.grid(which="major", linestyle="--", linewidth=0.5, color="gray", alpha=0.7)
        ax.legend()
        fig.tight_layout()
        return fig
    
    @staticmethod
    def create_custom_rate_chart(custom_series: pd.Series, 
                               rate_name: str, color: str = "darkgreen") -> plt.Figure:
        """Create chart for custom rate series"""
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(custom_series.index, custom_series, label="Custom Rate", 
                color=color, linewidth=2)
        ax.set_title(f"{rate_name} Over Time", fontsize=14)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Rate (%)", fontsize=12)
        ax.grid(which="major", linestyle="--", linewidth=0.5, color="gray", alpha=0.7)
        ax.legend()
        fig.tight_layout()
        return fig
    
    @staticmethod
    def create_fhlb_rate_curve(fhlb_df: pd.DataFrame) -> plt.Figure:
        """Create FHLB rate curve chart"""
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fhlb_df["Term"], fhlb_df["Regular Rate (%)"], 
                marker='o', linestyle='-', color='mediumblue')
        ax.set_title("Interest Rate Curve", fontsize=14)
        ax.set_xlabel("FHLB", fontsize=12)
        ax.set_ylabel("Rate (%)", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()
        return fig
    
    @staticmethod
    def create_cofi_yearly_chart(df_long: pd.DataFrame) -> alt.Chart:
        """Create Altair chart for yearly COFI rates"""
        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Rate:Q', title='Rate %', scale=alt.Scale(zero=False)),
            color=alt.Color('Term:N', title='Term'),
            tooltip=['Year', 'Term', 'Rate']
        ).properties(
            title='COFI Yearly Rates by Reset Term',
            width=700,
            height=400
        )
        return chart
    
    @staticmethod
    def create_cofi_monthly_chart(cofi_3_months: pd.DataFrame) -> alt.Chart:
        """Create Altair chart for monthly COFI rates"""
        chart = alt.Chart(cofi_3_months).transform_loess(
            'Date', 'COFI', bandwidth=0.5
        ).mark_line(
            color='steelblue'
        ).encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('COFI:Q', title='Rate %'),
            tooltip=['Date:T', 'COFI']
        ).properties(
            title='Soft evolution of 3-Month COFI',
            width=700,
            height=400
        )
        return chart
    
    @staticmethod
    def save_chart_to_buffer(fig: plt.Figure) -> io.BytesIO:
        """Save matplotlib figure to buffer for download"""
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return buf

    @staticmethod
    def create_user_login_bar_chart(user_summary: pd.DataFrame, top_n: int = 10) -> alt.Chart:
        """Create bar chart for user login counts using Altair"""
        if user_summary.empty:
            return alt.Chart(pd.DataFrame({'message': ['No data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(
                text='message:N'
            ).properties(
                width=400, height=200
            )
        
        top_users = user_summary.head(top_n)
        
        chart = alt.Chart(top_users).mark_bar(
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='lightblue', offset=0),
                       alt.GradientStop(color='darkblue', offset=1)]
            )
        ).encode(
            x=alt.X('username:N', 
                   sort=alt.EncodingSortField(field='Total Logins', order='descending'),
                   title='Username',
                   axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Total Logins:Q', title='Total Logins'),
            color=alt.Color('Total Logins:Q', 
                           scale=alt.Scale(scheme='viridis'),
                           legend=None),
            tooltip=['username:N', 'Total Logins:Q']
        ).properties(
            width=600,
            height=400,
            title=f'Top {min(top_n, len(top_users))} Users by Login Count'
        )
        
        return chart
    
    @staticmethod
    def create_daily_activity_line_chart(daily_activity: pd.DataFrame) -> alt.Chart:
        """Create line chart for daily login activity using Altair"""
        if daily_activity.empty:
            return alt.Chart(pd.DataFrame({'message': ['No data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(
                text='message:N'
            ).properties(
                width=400, height=200
            )
        
        daily_activity_copy = daily_activity.copy()
        daily_activity_copy['date_str'] = daily_activity_copy['date'].astype(str)
        
        line = alt.Chart(daily_activity_copy).mark_line(
            point=True, color='steelblue', strokeWidth=3
        ).encode(
            x=alt.X('date_str:T', title='Date', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('login_count:Q', title='Number of Logins'),
            tooltip=['date_str:T', 'login_count:Q']
        )
        
        if len(daily_activity_copy) > 3:
            trend = alt.Chart(daily_activity_copy).mark_line(
                color='red', strokeDash=[5, 5], opacity=0.7
            ).transform_regression('date_str', 'login_count').encode(
                x=alt.X('date_str:T'),
                y=alt.Y('login_count:Q')
            )
            
            chart = (line + trend).resolve_scale(
                color='independent'
            ).properties(
                width=600,
                height=400,
                title='Daily Login Activity with Trend'
            )
        else:
            chart = line.properties(
                width=600,
                height=400,
                title='Daily Login Activity'
            )
        
        return chart
    
    @staticmethod
    def create_activity_heatmap(heatmap_data: pd.DataFrame) -> alt.Chart:
        """Create heatmap for user activity using Altair"""
        if heatmap_data.empty:
            return alt.Chart(pd.DataFrame({'message': ['No data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(
                text='message:N'
            ).properties(
                width=400, height=200
            )
        
        heatmap_melted = heatmap_data.reset_index().melt(
            id_vars='username', 
            var_name='date', 
            value_name='login_count'
        )
        heatmap_melted['date'] = heatmap_melted['date'].astype(str)
        
        chart = alt.Chart(heatmap_melted).mark_rect().encode(
            x=alt.X('date:O', title='Date', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('username:N', title='Username'),
            color=alt.Color('login_count:Q', 
                           scale=alt.Scale(scheme='blues'),
                           title='Login Count'),
            tooltip=['username:N', 'date:O', 'login_count:Q']
        ).properties(
            width=600,
            height=max(400, len(heatmap_data.index) * 25),
            title='User Activity Heatmap'
        )
        
        return chart
    
    @staticmethod
    def create_user_activity_pie_chart(user_summary: pd.DataFrame, top_n: int = 8) -> alt.Chart:
        """Create pie chart for user activity distribution using Altair"""
        if user_summary.empty:
            return alt.Chart(pd.DataFrame({'message': ['No data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(
                text='message:N'
            ).properties(
                width=400, height=200
            )
        
        top_users = user_summary.head(top_n).copy()
        others_count = user_summary.iloc[top_n:]['Total Logins'].sum() if len(user_summary) > top_n else 0
        
        if others_count > 0:
            others_row = pd.DataFrame({
                'username': [f'Others ({len(user_summary) - top_n} users)'],
                'Total Logins': [others_count]
            })
            display_data = pd.concat([top_users[['username', 'Total Logins']], others_row], ignore_index=True)
        else:
            display_data = top_users[['username', 'Total Logins']]
        
        chart = alt.Chart(display_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta('Total Logins:Q'),
            color=alt.Color('username:N', 
                           scale=alt.Scale(scheme='category20'),
                           title='User'),
            tooltip=['username:N', 'Total Logins:Q']
        ).properties(
            width=400,
            height=400,
            title='Login Distribution by User'
        )
        
        return chart
    
    @staticmethod
    def create_login_frequency_histogram(user_summary: pd.DataFrame) -> alt.Chart:
        """Create histogram for login frequency distribution using Altair"""
        if user_summary.empty:
            return alt.Chart(pd.DataFrame({'message': ['No data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(
                text='message:N'
            ).properties(
                width=400, height=200
            )
        
        chart = alt.Chart(user_summary).mark_bar(
            color='steelblue', opacity=0.8
        ).encode(
            x=alt.X('Total Logins:Q', 
                   bin=alt.Bin(maxbins=20),
                   title='Number of Logins'),
            y=alt.Y('count():Q', title='Number of Users'),
            tooltip=['count():Q']
        ).properties(
            width=600,
            height=400,
            title='Distribution of Login Frequencies'
        )
        
        return chart



class ChartStyler:
    """Chart styling and customization utilities"""
    
    DEFAULT_COLORS = {
        'fred': 'steelblue',
        'custom': 'darkgreen', 
        'fhlb': 'mediumblue',
        'cofi': 'steelblue'
    }
    
    DEFAULT_FIGURE_SIZE = (10, 4)
    
    @classmethod
    def apply_default_style(cls, ax: plt.Axes, title: str, 
                          xlabel: str = "Date", ylabel: str = "Rate (%)"):
        """Apply default styling to matplotlib axes"""
        ax.set_title(title, fontsize=14)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(which="major", linestyle="--", linewidth=0.5, 
                color="gray", alpha=0.7)
    
    @classmethod
    def get_color(cls, chart_type: str) -> str:
        """Get default color for chart type"""
        return cls.DEFAULT_COLORS.get(chart_type, 'steelblue')