"""
SCENTIFY - Search Page
Search and filter perfumes with detailed view

IMPORTANT: Uses correct API field names (PascalCase with spaces)
- "Name", "Brand", "Image URL", "Main Accords", etc.
"""

import streamlit as st
from utils.api_client import search_fragrances
from utils.ui_helpers import display_perfume_card, display_perfume_detail
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

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "selected_perfume" not in st.session_state:
    st.session_state.selected_perfume = None

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

def track_perfume_click(perfume):
    """
    Track when a user clicks on a perfume for ML recommendations.
    Uses "Name" field from API.
    
    Args:
        perfume (dict): Perfume data from API
    """
    # API uses "Name" field (PascalCase)
    perfume_name = perfume.get("Name", "Unknown")
    
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
        # API uses "Name" field
        perfume_name = perfume.get("Name", "")
        # Check if already in inventory
        is_in_inventory = any(p.get("Name") == perfume_name for p in st.session_state.user_inventory)
        
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
            placeholder="e.g., Chanel, Dior, Sauvage...",
            key="search_input_field"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Search", use_container_width=True, type="primary")
    
    st.write("")
    
    # ========================================================================
    # PERFORM SEARCH
    # ========================================================================
    
    # Trigger search on button click or when input changes (with min 3 chars)
    if search_button or (search_input != st.session_state.search_query and len(search_input) >= 3):
        st.session_state.search_query = search_input
        
        if len(search_input) >= 3:
            # Perform search
            with st.spinner("Searching perfumes..."):
                results = search_fragrances(search_input, limit=20)
                
                # Rank results using ML recommender if user has click history
                if st.session_state.clicked_perfumes and results:
                    results = rank_results(results)
                
                st.session_state.search_results = results
        else:
            st.warning("Please enter at least 3 characters to search.")
    
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
                        # Use "Name" field for unique key
                        perfume_name = perfume.get("Name", f"perfume_{i+j}")
                        if st.button(
                            "View Details", 
                            key=f"view_{i+j}_{perfume_name}", 
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
        st.info("No results found. Try a different search term.")
    
    else:
        # No search performed yet
        st.info("👆 Enter a search term above to find perfumes")
        st.write("")
        st.write("")
        
        # Show some examples
        st.markdown("### 💡 Try searching for:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("- **Chanel No. 5**")
            st.markdown("- **Dior Sauvage**")
        
        with col2:
            st.markdown("- **Tom Ford**")
            st.markdown("- **Versace**")
        
        with col3:
            st.markdown("- **floral**")
            st.markdown("- **woody**")

