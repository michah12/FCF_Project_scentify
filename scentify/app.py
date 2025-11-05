"""
SCENTIFY - Perfume Finder & Recommendation App
Landing Page (Main Entry Point)

This is the main entry point for the Streamlit application.
It displays the landing page with navigation to three main features:
1. Search - Find perfumes by name, brand, or filters
2. Questionnaire - Get recommendations based on preferences
3. Perfume Inventory - Manage your personal collection and see analytics
"""

import streamlit as st
import requests
from utils.api_client import get_usage

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="SCENTIFY - Perfume Finder",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Initialize session state variables if they don't exist
# This ensures data persists across page navigations within the same session

if "user_inventory" not in st.session_state:
    # List to store user's saved perfumes
    st.session_state.user_inventory = []

if "clicked_perfumes" not in st.session_state:
    # Dictionary to track which perfumes the user has clicked (for ML recommendations)
    # Format: {perfume_name: click_count}
    st.session_state.clicked_perfumes = {}

if "user_profile" not in st.session_state:
    # User profile vector for ML-based recommendations
    # Will be built from clicked perfumes' accord vectors
    st.session_state.user_profile = None

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main background - light floral theme */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #fff5f7 100%);
    }
    
    /* Title styling */
    .main-title {
        font-size: 4rem;
        font-weight: 700;
        color: #d4567b;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Playfair Display', serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: #8b5a7c;
        text-align: center;
        margin-bottom: 3rem;
        font-style: italic;
    }
    
    /* Card styling for navigation buttons */
    .nav-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
        height: 100%;
        border: 2px solid #f5e6ea;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(212, 86, 123, 0.2);
        border-color: #d4567b;
    }
    
    .nav-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .nav-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #d4567b;
        margin-bottom: 0.5rem;
    }
    
    .nav-description {
        font-size: 1rem;
        color: #666;
        line-height: 1.5;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 4rem;
        padding: 2rem;
        color: #8b5a7c;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Display main title and subtitle
st.markdown('<div class="main-title">🌸 SCENTIFY 🌸</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Discover Your Perfect Fragrance</div>', unsafe_allow_html=True)

# Add some spacing
st.write("")
st.write("")

# Create three columns for the main navigation cards
col1, col2, col3 = st.columns(3, gap="large")

# ============================================================================
# NAVIGATION CARD 1: SEARCH
# ============================================================================

with col1:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">🔍</div>
        <div class="nav-title">Search</div>
        <div class="nav-description">
            Find perfumes by name, brand, or use advanced filters 
            to discover your next signature scent.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    # Button to navigate to Search page
    if st.button("Explore Perfumes", key="btn_search", use_container_width=True):
        st.switch_page("pages/01_Search.py")

# ============================================================================
# NAVIGATION CARD 2: QUESTIONNAIRE
# ============================================================================

with col2:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">📋</div>
        <div class="nav-title">Questionnaire</div>
        <div class="nav-description">
            Answer a few questions about your preferences and let our 
            AI recommend the perfect fragrances for you.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    # Button to navigate to Questionnaire page
    if st.button("Get Recommendations", key="btn_quiz", use_container_width=True):
        st.switch_page("pages/02_Questionnaire.py")

# ============================================================================
# NAVIGATION CARD 3: INVENTORY
# ============================================================================

with col3:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">📚</div>
        <div class="nav-title">Perfume Inventory</div>
        <div class="nav-description">
            Manage your personal fragrance collection and visualize 
            your scent profile with beautiful analytics.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    # Button to navigate to Inventory page
    # Show count of saved perfumes if any exist
    inventory_count = len(st.session_state.user_inventory)
    button_text = f"My Collection ({inventory_count})" if inventory_count > 0 else "My Collection"
    if st.button(button_text, key="btn_inventory", use_container_width=True):
        st.switch_page("pages/03_Inventory.py")

# ============================================================================
# FOOTER WITH API USAGE INFO
# ============================================================================

st.write("")
st.write("")
st.write("")

# Try to fetch and display API usage information (optional)
try:
    usage_data = get_usage()
    if usage_data and "requests_remaining" in usage_data:
        remaining = usage_data["requests_remaining"]
        st.markdown(f"""
        <div class="footer">
            <p>Powered by Fragella API • {remaining:,} API requests remaining today</p>
            <p style="font-size: 0.8rem; margin-top: 0.5rem;">
                Built with Streamlit • Data updates in real-time
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback if API call fails
        st.markdown("""
        <div class="footer">
            <p>Powered by Fragella API</p>
            <p style="font-size: 0.8rem; margin-top: 0.5rem;">
                Built with Streamlit • Data updates in real-time
            </p>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    # If API is unavailable, show footer without usage info
    st.markdown("""
    <div class="footer">
        <p>Powered by Fragella API</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            Built with Streamlit • Data updates in real-time
        </p>
    </div>
    """, unsafe_allow_html=True)

