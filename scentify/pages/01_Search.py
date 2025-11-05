"""
SCENTIFY - Search Page
Search and filter perfumes with detailed view

This page allows users to:
- Search for perfumes by name
- Apply filters (brand, price, gender, scent type/accords)
- View search results with images and basic info
- Click on a perfume to see detailed information
- Track clicks for ML-based recommendations
"""

import streamlit as st
import pandas as pd
from utils.api_client import search_fragrances, search_accords, search_notes
from utils.ui_helpers import display_perfume_card, display_perfume_detail, get_transparent_image_url
from utils.recommender import update_user_profile, rank_results

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Search - SCENTIFY",
    page_icon="🔍",
    layout="wide"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Initialize session state for search and filters
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "selected_perfume" not in st.session_state:
    # Stores the currently selected perfume for detail view
    st.session_state.selected_perfume = None

if "filter_brand" not in st.session_state:
    st.session_state.filter_brand = ""

if "filter_gender" not in st.session_state:
    st.session_state.filter_gender = "All"

if "filter_price_range" not in st.session_state:
    st.session_state.filter_price_range = (0, 500)

if "filter_accords" not in st.session_state:
    st.session_state.filter_accords = []

if "clicked_perfumes" not in st.session_state:
    st.session_state.clicked_perfumes = {}

if "user_inventory" not in st.session_state:
    st.session_state.user_inventory = []

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #fff5f7 100%);
    }
    
    .search-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #d4567b;
        margin-bottom: 1rem;
    }
    
    .filter-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .result-count {
        font-size: 1.2rem;
        color: #8b5a7c;
        margin-bottom: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def perform_search(query, filters=None):
    """
    Perform search using Fragella API with optional filters.
    
    Args:
        query (str): Search query string
        filters (dict): Optional filters (brand, gender, price, accords)
    
    Returns:
        list: List of perfume dictionaries
    """
    if len(query) < 3:
        st.warning("Please enter at least 3 characters to search.")
        return []
    
    try:
        # Call Fragella API
        results = search_fragrances(query)
        
        if not results:
            st.info("No perfumes found. Try a different search term.")
            return []
        
        # Apply client-side filters if provided
        if filters:
            filtered_results = results.copy()
            
            # Filter by brand
            if filters.get("brand"):
                filtered_results = [
                    p for p in filtered_results 
                    if p.get("brand", "").lower() == filters["brand"].lower()
                ]
            
            # Filter by gender
            if filters.get("gender") and filters["gender"] != "All":
                filtered_results = [
                    p for p in filtered_results 
                    if filters["gender"].lower() in p.get("gender", "").lower()
                ]
            
            # Filter by price range (if price data available)
            if filters.get("price_range"):
                min_price, max_price = filters["price_range"]
                filtered_results = [
                    p for p in filtered_results 
                    if min_price <= p.get("price", 0) <= max_price or p.get("price") is None
                ]
            
            # Filter by accords
            if filters.get("accords"):
                filtered_results = [
                    p for p in filtered_results
                    if any(
                        accord.lower() in [a.get("name", "").lower() 
                        for a in p.get("main_accords", [])]
                        for accord in filters["accords"]
                    )
                ]
            
            return filtered_results
        
        return results
        
    except Exception as e:
        st.error(f"Error searching perfumes: {str(e)}")
        return []

def track_perfume_click(perfume):
    """
    Track when a user clicks on a perfume for ML recommendations.
    
    Args:
        perfume (dict): Perfume data dictionary
    """
    perfume_name = perfume.get("name", "Unknown")
    
    # Increment click count
    if perfume_name in st.session_state.clicked_perfumes:
        st.session_state.clicked_perfumes[perfume_name] += 1
    else:
        st.session_state.clicked_perfumes[perfume_name] = 1
    
    # Update user profile for ML recommendations
    update_user_profile(perfume)

# ============================================================================
# MAIN CONTENT - DETAIL VIEW
# ============================================================================

# If a perfume is selected, show detail view
if st.session_state.selected_perfume is not None:
    perfume = st.session_state.selected_perfume
    
    # Back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back", key="back_to_results"):
            st.session_state.selected_perfume = None
            st.rerun()
    
    # Display detailed perfume information
    display_perfume_detail(perfume)
    
    # Add to inventory button
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        perfume_name = perfume.get("name", "")
        # Check if already in inventory
        is_in_inventory = any(p.get("name") == perfume_name for p in st.session_state.user_inventory)
        
        if is_in_inventory:
            st.success("✓ Already in your collection")
        else:
            if st.button("➕ Add to My Collection", use_container_width=True, type="primary"):
                st.session_state.user_inventory.append(perfume)
                st.success("Added to your collection!")
                st.rerun()

# ============================================================================
# MAIN CONTENT - SEARCH & RESULTS VIEW
# ============================================================================

else:
    # Page title
    st.markdown('<div class="search-title">🔍 Search Perfumes</div>', unsafe_allow_html=True)
    
    # Back to home button
    if st.button("← Back to Home"):
        st.switch_page("app.py")
    
    st.write("")
    
    # ========================================================================
    # SEARCH BAR
    # ========================================================================
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_input = st.text_input(
            "Search by perfume name, brand, or keyword",
            value=st.session_state.search_query,
            placeholder="e.g., Chanel, rose, woody...",
            key="search_input_field"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Search", use_container_width=True, type="primary")
    
    st.write("")
    
    # ========================================================================
    # FILTER SECTION
    # ========================================================================
    
    with st.expander("🎛️ Advanced Filters", expanded=False):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Brand filter
            brand_input = st.text_input(
                "Brand",
                value=st.session_state.filter_brand,
                placeholder="e.g., Dior, Chanel...",
                key="brand_filter"
            )
        
        with filter_col2:
            # Gender filter
            gender_options = ["All", "Male", "Female", "Unisex"]
            gender_select = st.selectbox(
                "Gender",
                options=gender_options,
                index=gender_options.index(st.session_state.filter_gender),
                key="gender_filter"
            )
        
        with filter_col3:
            # Price range filter
            price_range = st.slider(
                "Price Range ($)",
                min_value=0,
                max_value=500,
                value=st.session_state.filter_price_range,
                step=10,
                key="price_filter"
            )
        
        st.write("")
        
        # Accord/Scent type filter
        st.markdown("**Scent Type (Accords)**")
        accord_col1, accord_col2, accord_col3, accord_col4 = st.columns(4)
        
        # Common accord options
        common_accords = [
            "Floral", "Woody", "Citrus", "Fresh", "Spicy", "Sweet", "Fruity", 
            "Aromatic", "Aquatic", "Green", "Oriental", "Amber", "Vanilla"
        ]
        
        selected_accords = []
        
        with accord_col1:
            for accord in common_accords[:4]:
                if st.checkbox(accord, key=f"accord_{accord}"):
                    selected_accords.append(accord)
        
        with accord_col2:
            for accord in common_accords[4:8]:
                if st.checkbox(accord, key=f"accord_{accord}"):
                    selected_accords.append(accord)
        
        with accord_col3:
            for accord in common_accords[8:11]:
                if st.checkbox(accord, key=f"accord_{accord}"):
                    selected_accords.append(accord)
        
        with accord_col4:
            for accord in common_accords[11:]:
                if st.checkbox(accord, key=f"accord_{accord}"):
                    selected_accords.append(accord)
        
        st.write("")
        
        # Apply filters button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            apply_filters_btn = st.button("Apply Filters", use_container_width=True)
    
    # ========================================================================
    # PERFORM SEARCH
    # ========================================================================
    
    # Trigger search on button click or Enter key
    if search_button or (search_input != st.session_state.search_query and len(search_input) >= 3):
        st.session_state.search_query = search_input
        
        # Build filters dictionary
        filters = {
            "brand": brand_input,
            "gender": gender_select,
            "price_range": price_range,
            "accords": selected_accords
        }
        
        # Update session state filters
        st.session_state.filter_brand = brand_input
        st.session_state.filter_gender = gender_select
        st.session_state.filter_price_range = price_range
        st.session_state.filter_accords = selected_accords
        
        # Perform search
        with st.spinner("Searching perfumes..."):
            results = perform_search(search_input, filters)
            
            # Rank results using ML recommender if user has click history
            if st.session_state.clicked_perfumes:
                results = rank_results(results)
            
            st.session_state.search_results = results
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    if st.session_state.search_results:
        results = st.session_state.search_results
        
        # Show result count
        st.markdown(f'<div class="result-count">Found {len(results)} perfume(s)</div>', 
                   unsafe_allow_html=True)
        
        # Display results in grid (3 columns)
        for i in range(0, len(results), 3):
            cols = st.columns(3)
            
            for j, col in enumerate(cols):
                if i + j < len(results):
                    perfume = results[i + j]
                    
                    with col:
                        # Display perfume card
                        display_perfume_card(perfume)
                        
                        # View details button
                        if st.button(
                            "View Details", 
                            key=f"view_{i+j}_{perfume.get('name', '')}", 
                            use_container_width=True
                        ):
                            # Track click for ML recommendations
                            track_perfume_click(perfume)
                            
                            # Set selected perfume and rerun to show detail view
                            st.session_state.selected_perfume = perfume
                            st.rerun()
            
            st.write("")
    
    elif st.session_state.search_query:
        # Search was performed but no results
        st.info("No results found. Try adjusting your search or filters.")
    
    else:
        # No search performed yet
        st.info("👆 Enter a search term above to find perfumes")

