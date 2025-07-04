
"""
Financial Glossary Module for Banking Rates Dashboard
Updated with safe session state management to prevent attribute errors
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import io
from typing import Dict, List, Tuple, Optional
from constants.glossary_content import financial_rates, quick_terms, sections_terms, introduction, generate_rate_card, style


def safe_session_get(key: str, default=None):
    """Safely get a session state value with fallback"""
    try:
        return getattr(st.session_state, key, default)
    except AttributeError:
        return default


def safe_session_set(key: str, value):
    """Safely set a session state value"""
    try:
        setattr(st.session_state, key, value)
        return True
    except AttributeError:
        return False


def ensure_session_key(key: str, default=None):
    """Ensure a session state key exists"""
    if not hasattr(st.session_state, key):
        safe_session_set(key, default)


class FinancialGlossary:
    """Main class to handle the financial glossary with safe session state"""
    
    def __init__(self):
        self.financial_rates = financial_rates
        
        self.quick_terms = quick_terms
        
        self.section_terms = sections_terms
        
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize all required session state variables safely"""
        session_defaults = {
            'favorite_terms': [],
            'term_views': {},
            'show_term_detail': None,
            'current_section': 'FRED Rates',
            'glossary_search_query': '',
            'selected_category': 'Todos',
            'glossary_sort_by': 'Alfabético',
            'glossary_expanded': False
        }
        
        for key, default_value in session_defaults.items():
            ensure_session_key(key, default_value)

    def apply_custom_css(self):
        """Applies custom CSS styles for the glossary"""
        st.markdown(style, unsafe_allow_html=True)

    def get_term_definition(self, term_key: str) -> str:
        """Returns the definition of a glossary term"""
        for rate_name, rate_info in self.financial_rates.items():
            if term_key.upper() in rate_name.upper():
                return rate_info["description"]
        return "Term not found in the glossary"

    def track_term_view(self, term: str):
        """Tracks term views safely"""
        term_views = safe_session_get('term_views', {})
        if term in term_views:
            term_views[term] += 1
        else:
            term_views[term] = 1
        safe_session_set('term_views', term_views)

    def render_sidebar_glossary(self):
        """Renders the quick glossary in the sidebar"""
        self._initialize_session_state()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📚 Quick Glossary")
        
        for term, definition in self.quick_terms.items():
            with st.sidebar.expander(f"🔍 {term}"):
                st.markdown(f'<div class="quick-term">{definition}</div>', unsafe_allow_html=True)
                if st.button(f"⭐ Favorite", key=f"fav_btn_{term}"):
                    self.toggle_favorite(term)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("🔍 **Quick Search**")
        search_query = st.sidebar.text_input(
            "Search term", 
            placeholder="e.g. SOFR",
            value=safe_session_get('glossary_search_query', ''),
            key="sidebar_search"
        )
        safe_session_set('glossary_search_query', search_query)
        
        if search_query:
            matches = self.search_terms(search_query)
            if matches:
                st.sidebar.markdown("**Results:**")
                for name, desc in matches[:3]:
                    st.sidebar.markdown(f"**{name.split('(')[0]}**")
                    st.sidebar.caption(desc)
            else:
                st.sidebar.info("No terms found")
        
        
        self.render_favorites_sidebar()
        
        self.render_popular_terms_sidebar()
        
        if st.sidebar.button("📖 View Full Glossary", use_container_width=True):
            safe_session_set('current_section', "📚 Financial Glossary")
            st.rerun()

    def render_favorites_sidebar(self):
        """Renders the favorites section in the sidebar safely"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("⭐ **Favorite Terms**")
        
        favorite_terms = safe_session_get('favorite_terms', [])
        
        if favorite_terms:
            for i, term in enumerate(favorite_terms):
                col1, col2 = st.sidebar.columns([4, 1])
                with col1:
                    if st.button(term, key=f"show_fav_{term}_{i}"):
                        safe_session_set('show_term_detail', term)
                        self.track_term_view(term)
                with col2:
                    if st.button("❌", key=f"remove_fav_{term}_{i}"):
                        updated_favorites = [t for t in favorite_terms if t != term]
                        safe_session_set('favorite_terms', updated_favorites)
                        st.rerun()
        else:
            st.sidebar.info("No favorite terms")

    def render_popular_terms_sidebar(self):
        """Renders the most viewed terms in the sidebar safely"""
        term_views = safe_session_get('term_views', {})
        
        if term_views:
            st.sidebar.markdown("---")
            st.sidebar.markdown("📈 **Most Viewed**")
            sorted_terms = sorted(term_views.items(), key=lambda x: x[1], reverse=True)
            
            for term, count in sorted_terms[:5]:
                st.sidebar.markdown(f"• {term} ({count})")

    def toggle_favorite(self, term: str):
        """Adds or removes a term from favorites safely"""
        favorite_terms = safe_session_get('favorite_terms', [])
        
        if term in favorite_terms:
            updated_favorites = [t for t in favorite_terms if t != term]
            safe_session_set('favorite_terms', updated_favorites)
            st.success(f"Removed from favorites: {term}")
        else:
            updated_favorites = favorite_terms + [term]
            safe_session_set('favorite_terms', updated_favorites)
            st.success(f"Added to favorites: {term}")

    def search_terms(self, query: str) -> List[Tuple[str, str]]:
        """Searches for terms in the glossary"""
        matches = []
        search_lower = query.lower()
        
        for rate_name, rate_info in self.financial_rates.items():
            if search_lower in rate_name.lower() or search_lower in rate_info["description"].lower():
                matches.append((rate_name, rate_info["description"][:100] + "..."))
        
        return matches

    def add_section_specific_glossary(self, section_name: str):
        """Adds section-specific terms"""
        self._initialize_session_state()
        
        if section_name in self.section_terms:
            with st.expander("💡 Relevant Terms in This Section"):
                col1, col2 = st.columns(2)
                terms = self.section_terms[section_name]
                
                for i, term in enumerate(terms):
                    with col1 if i % 2 == 0 else col2:
                        if term in self.quick_terms:
                            st.markdown(f"**{term}**: {self.quick_terms[term]}")
                            if st.button("⭐", key=f"section_fav_{term}_{section_name}_{i}", help="Add to favorites"):
                                self.toggle_favorite(term)
                        else:
                            definition = self.get_term_definition(term)
                            if definition != "Term not found in the glossary":
                                st.markdown(f"**{term}**: {definition[:80]}...")
                                if st.button("⭐", key=f"section_fav_full_{term}_{section_name}_{i}", help="Add to favorites"):
                                    self.toggle_favorite(term)

    def filter_and_sort_rates(self, selected_category: str, search_term: str, sort_by: str) -> Dict:
        """Filters and sorts rates according to criteria"""
        filtered_rates = self.financial_rates.copy()
        
        if selected_category != "Todos":
            filtered_rates = {k: v for k, v in filtered_rates.items() 
                            if v["category"] == selected_category}
        
        if search_term:
            search_lower = search_term.lower()
            filtered_rates = {
                k: v for k, v in filtered_rates.items() 
                if search_lower in k.lower() or search_lower in v["description"].lower()
            }
        
        
        if sort_by == "Alfabético":
            sorted_rates = dict(sorted(filtered_rates.items()))
        elif sort_by == "Por Categoría":
            sorted_rates = dict(sorted(filtered_rates.items(), key=lambda x: x[1]["category"]))
        else:  
            impact_order = ["Monetary Policy", "Reference Rate", "Government Securities", 
                          "Commercial Banking", "Consumer Finance", "Mortgage Finance", 
                          "Derivative Rate", "Legacy Reference Rate", "Government Sponsored Enterprise",
                          "Regional Index", "Data Source"]
            sorted_rates = dict(sorted(filtered_rates.items(), 
                                     key=lambda x: impact_order.index(x[1]["category"]) 
                                     if x[1]["category"] in impact_order else 999))
        
        return sorted_rates

    def render_full_glossary(self):
        """Renders the full glossary"""
        self._initialize_session_state()
        
        self.apply_custom_css()
        
        st.markdown('<h1 class="glossary-header">📊 Full Financial Glossary</h1>', 
                   unsafe_allow_html=True)
        
        st.markdown(introduction, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            categories = ["Todos"] + sorted(list(set([rate["category"] for rate in self.financial_rates.values()])))
            selected_category = st.selectbox(
                "Category", 
                categories,
                index=categories.index(safe_session_get('selected_category', 'Todos')) if safe_session_get('selected_category', 'Todos') in categories else 0,
                key="full_glossary_category"
            )
            safe_session_set('selected_category', selected_category)
        
        with col2:
            search_term = st.text_input(
                "🔎 Search", 
                placeholder="Name or keyword...",
                value=safe_session_get('glossary_search_query', ''),
                key="full_glossary_search"
            )
            safe_session_set('glossary_search_query', search_term)
        
        with col3:
            sort_options = ["Alfabético", "Por Categoría", "Por Impacto"]
            current_sort = safe_session_get('glossary_sort_by', 'Alfabético')
            sort_by = st.selectbox(
                "Sort by", 
                sort_options,
                index=sort_options.index(current_sort) if current_sort in sort_options else 0,
                key="full_glossary_sort"
            )
            safe_session_set('glossary_sort_by', sort_by)
        
        with col4:
            export_format = st.selectbox("Export", ["Select", "JSON", "CSV"])
            if export_format != "Select":
                self.export_glossary(export_format)
        
        sorted_rates = self.filter_and_sort_rates(selected_category, search_term, sort_by)
        
        st.markdown(f"**Showing {len(sorted_rates)} of {len(self.financial_rates)} rates**")
        
        favorite_terms = safe_session_get('favorite_terms', [])
        if favorite_terms:
            with st.expander(f"⭐ Your Favorites ({len(favorite_terms)} terms)", expanded=False):
                for i, term in enumerate(favorite_terms):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{term}**")
                        definition = self.get_term_definition(term)
                        if definition != "Term not found in the glossary":
                            st.caption(definition[:100] + "...")
                    with col2:
                        if st.button("❌", key=f"full_remove_fav_{term}_{i}", help="Remove from favorites"):
                            updated_favorites = [t for t in favorite_terms if t != term]
                            safe_session_set('favorite_terms', updated_favorites)
                            st.rerun()
        
        for rate_name, rate_info in sorted_rates.items():
            self.render_rate_card(rate_name, rate_info)
        
        self.render_summary_statistics()
        self.render_category_chart_matplotlib()

    def render_rate_card(self, rate_name: str, rate_info: Dict):
        """Renders an individual rate card"""
        term_name = rate_name.split('(')[0].strip()
        self.track_term_view(term_name)
        
        st.markdown(generate_rate_card(rate_name, rate_info), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            unique_key = f"fav_card_{abs(hash(rate_name))}"
            if st.button("⭐", key=unique_key, help="Add to favorites"):
                self.toggle_favorite(term_name)
        with col2:
            copy_key = f"copy_{abs(hash(rate_name))}"
            if st.button("📋", key=copy_key, help="Copy definition"):
                st.info("Definition copied to clipboard")

    def render_summary_statistics(self):
        """Renders summary statistics"""
        st.markdown("---")
        st.markdown("### 📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rates", len(self.financial_rates))
        
        with col2:
            categories_count = len(set([rate["category"] for rate in self.financial_rates.values()]))
            st.metric("Categories", categories_count)
        
        with col3:
            active_rates = len([rate for rate in self.financial_rates.values() 
                              if "legacy" not in rate["current_use"].lower()])
            st.metric("Active Rates", active_rates)
        
        with col4:
            term_views = safe_session_get('term_views', {})
            total_views = sum(term_views.values()) if term_views else 0
            st.metric("Total Views", total_views)

    def render_category_chart_matplotlib(self):
        """Renders the category distribution chart using matplotlib"""
        st.markdown("### 📊 Category Distribution")
        
        category_counts = {}
        for rate_info in self.financial_rates.values():
            category = rate_info["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                 '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
        wedges, texts, autotexts = ax.pie(counts, labels=categories, autopct='%1.1f%%', 
                                         colors=colors[:len(categories)], startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title("Distribution of Financial Rates by Category", 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        st.pyplot(fig)
        
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        st.download_button(
            label="📥 Download Chart",
            data=buf.getvalue(),
            file_name="category_distribution.png",
            mime="image/png"
        )

    def export_glossary(self, format_type: str):
        """Exports the glossary in different formats"""
        if format_type == "JSON":
            json_data = json.dumps(self.financial_rates, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Download JSON",
                json_data,
                "glossary.json",
                "application/json",
                key="download_json"
            )
        elif format_type == "CSV":
            df = pd.DataFrame.from_dict(self.financial_rates, orient='index')
            csv = df.to_csv(encoding='utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                "glossary.csv",
                "text/csv",
                key="download_csv"
            )

    def create_term_tooltip(self, term: str, definition_key: Optional[str] = None) -> str:
        """Creates a tooltip for technical terms"""
        if definition_key:
            definition = self.get_term_definition(definition_key)
            return f'<span class="term-tooltip" title="{definition[:100]}...">{term}</span>'
        return f'<span class="term-tooltip">{term}</span>'


try:
    glossary = FinancialGlossary()
except Exception as e:
    print(f"Warning: Could not initialize glossary: {e}")
    glossary = None


def render_sidebar_glossary():
    """Convenience function to render the sidebar safely"""
    try:
        if glossary:
            return glossary.render_sidebar_glossary()
        else:
            st.sidebar.info("Glossary not available")
    except Exception as e:
        st.sidebar.error(f"Glossary error: {str(e)}")


def render_full_glossary():
    """Convenience function to render the full glossary safely"""
    try:
        if glossary:
            return glossary.render_full_glossary()
        else:
            st.error("Glossary not available")
    except Exception as e:
        st.error(f"Glossary error: {str(e)}")


def add_section_glossary(section_name: str):
    """Convenience function to add section-specific terms safely"""
    try:
        if glossary:
            return glossary.add_section_specific_glossary(section_name)
    except Exception as e:
        st.info(f"Section glossary not available: {str(e)}")


def get_term_definition(term: str) -> str:
    """Convenience function to get definitions safely"""
    try:
        if glossary:
            return glossary.get_term_definition(term)
        return "Glossary not available"
    except Exception as e:
        return f"Error getting definition: {str(e)}"


def create_term_tooltip(term: str, definition_key: Optional[str] = None) -> str:
    """Convenience function to create tooltips safely"""
    try:
        if glossary:
            return glossary.create_term_tooltip(term, definition_key)
        return term
    except Exception as e:
        return term