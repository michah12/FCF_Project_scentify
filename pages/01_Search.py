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
# IMPORTS AND PAGE CONFIGURATION
# ============================================================================

import re

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

def _extract_price(value):
    """
    Try to parse a numeric price from API value which may be numeric or string like '$120'.
    Returns float or None.
    """
    if value is None:
        return None
    try:
        # direct numeric
        return float(value)
    except Exception:
        # try to find digits
        m = re.search(r"[\d,.]+", str(value))
        if m:
            return float(m.group(0).replace(",", ""))
    return None

def _normalize_list_field(field):
    """Return a list of normalized tokens from a field (list or comma/string)."""
    if not field:
        return []
    if isinstance(field, (list, tuple)):
        return [str(x).strip() for x in field if x]
    # split comma or semicolon separated strings
    return [s.strip() for s in re.split(r"[;,]", str(field)) if s.strip()]

def get_brands_and_notes_from_results(results):
    """Collect unique brands and main accords/notes from provided results."""
    brands = set()
    notes = set()
    for p in results:
        b = p.get("Brand") or p.get("brand") or p.get("Manufacturer")
        if b:
            brands.add(str(b).strip())
        # main accords / notes
        accords = _normalize_list_field(p.get("Main Accords") or p.get("MainAccords") or p.get("Notes"))
        for a in accords:
            notes.add(a)
    return sorted(brands), sorted(notes)

def apply_filters(results, brand="All Brands", price_range=(0, 9999), gender="Any", selected_notes=None):
    """Filter a list of perfume dicts by brand, price, gender, and notes/accords."""
    if selected_notes is None:
        selected_notes = []
    filtered = []
    min_p, max_p = price_range
    for p in results:
        # Brand filter
        b = (p.get("Brand") or p.get("brand") or "").strip()
        if brand != "All Brands" and b != brand:
            continue
        # Price filter
        price_val = _extract_price(p.get("Price") or p.get("price"))
        if price_val is not None:
            if not (min_p <= price_val <= max_p):
                continue
        else:
            # if no price, include by default; change this line if you want to exclude unknown prices
            pass
        # Gender filter
        g = str(p.get("Gender") or p.get("gender") or "").lower()
        if gender != "Any":
            # Accept common variants
            if gender.lower() == "women" and "women" not in g and "female" not in g:
                continue
            if gender.lower() == "man" and "men" not in g and "male" not in g:
                continue
            if gender.lower() == "unisex" and "unisex" not in g:
                continue
        # Notes/Accords filter
        accords = [a.lower() for a in _normalize_list_field(p.get("Main Accords") or p.get("MainAccords") or p.get("Notes"))]
        if selected_notes:
            # require that at least one selected note is present
            match = False
            for n in selected_notes:
                if n.lower() in accords:
                    match = True
                    break
            if not match:
                continue
        filtered.append(p)
    return filtered

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
    
    # Initialize filter state if not present
    if 'all_results_for_filters' not in st.session_state:
        st.session_state.all_results_for_filters = []
        
    # Show filters when we have search results
    all_results_for_filters = []
    try:
        # try to fetch a broader set for filter options (best-effort)
        all_results_for_filters = search_fragrances("", limit=500) or []
        st.session_state.all_results_for_filters = all_results_for_filters
    except Exception:
        # fallback to current search results
        all_results_for_filters = st.session_state.search_results or []
    
    # Collect brands and notes for filter selectors
    brands_list, notes_list = get_brands_and_notes_from_results(all_results_for_filters or st.session_state.search_results or [])
    if not brands_list:
        brands_list = ["Unknown"]
    brands_options = ["All Brands"] + brands_list
    
    # Determine price bounds from available dataset
    prices = []
    for p in (all_results_for_filters or st.session_state.search_results or []):
        v = _extract_price(p.get("Price") or p.get("price"))
        if v is not None:
            prices.append(v)
    if prices:
        min_price_avail, max_price_avail = int(min(prices)), int(max(prices))
    else:
        min_price_avail, max_price_avail = 0, 500
    
    # Render filter controls
    with st.expander("Filters", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns([3, 3, 2, 4])
        with fcol1:
            selected_brand = st.selectbox("Brand", options=brands_options, index=0, key="filter_brand")
        with fcol2:
            selected_price = st.slider("Price", min_value=min_price_avail, max_value=max_price_avail,
                                       value=(min_price_avail, max_price_avail), step=1, key="filter_price")
        with fcol3:
            selected_gender = st.selectbox("Gender", options=["Any", "Women", "Man", "Unisex"], index=0, key="filter_gender")
        with fcol4:
            selected_notes = st.multiselect("Notes / Main Accords", options=notes_list, default=[], key="filter_notes")
    
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
        
        # Apply filters
        filtered_results = apply_filters(results, brand=selected_brand, price_range=selected_price,
                                      gender=selected_gender, selected_notes=selected_notes)
        
        # Re-rank filtered results if recommender has history
        if st.session_state.clicked_perfumes and filtered_results:
            filtered_results = rank_results(filtered_results)
        
        # Show result count
        st.markdown(f'<div class="result-count">Found {len(filtered_results)} perfume(s) (filtered)</div>', 
                   unsafe_allow_html=True)
        
        # Display results in grid (3 columns)
        for i in range(0, len(filtered_results), 3):
            cols = st.columns(3)
            
            for j, col in enumerate(cols):
                if i + j < len(filtered_results):
                    perfume = filtered_results[i + j]
                    
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
