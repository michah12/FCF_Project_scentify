"""
SCENTIFY - Perfume Inventory Page
Manage personal collection with visual analytics

Uses correct API fields:
- "Name", "Brand", "Main Accords"
- "Notes" object with "Top", "Middle", "Base" arrays
- "Season Ranking", "Occasion Ranking" arrays
"""

import streamlit as st
import plotly.graph_objects as go
from collections import Counter
from utils.api_client import search_fragrances
from utils.ui_helpers import display_perfume_card, display_perfume_detail, create_note_donut_chart, create_bar_chart

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="My Collection - SCENTIFY",
    page_icon="📚",
    layout="wide"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "user_inventory" not in st.session_state:
    st.session_state.user_inventory = []

if "selected_perfume" not in st.session_state:
    st.session_state.selected_perfume = None

if "show_add_perfume" not in st.session_state:
    st.session_state.show_add_perfume = False

if "add_search_query" not in st.session_state:
    st.session_state.add_search_query = ""

if "add_search_results" not in st.session_state:
    st.session_state.add_search_results = []

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #fff5f7 100%);
    }
    
    .inventory-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #d4567b;
        margin-bottom: 1rem;
    }
    
    .stats-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 2px solid #f5e6ea;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #d4567b;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #8b5a7c;
        margin-top: 0.5rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #d4567b;
        margin: 2rem 0 1rem 0;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem;
        background: white;
        border-radius: 15px;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_notes_from_inventory():
    """
    Extract and count all notes from user's inventory.
    API returns "Notes" object with "Top", "Middle", "Base" arrays.
    Each note is an object: {"name": "...", "imageUrl": "..."}
    
    Returns:
        tuple: (top_notes_counter, heart_notes_counter, base_notes_counter)
    """
    top_notes = []
    heart_notes = []
    base_notes = []
    
    for perfume in st.session_state.user_inventory:
        # Get Notes object
        notes_obj = perfume.get("Notes", {})
        
        # Extract top notes
        top_notes_list = notes_obj.get("Top", [])
        for note_obj in top_notes_list:
            note_name = note_obj.get("name")
            if note_name:
                top_notes.append(note_name)
        
        # Extract middle/heart notes
        middle_notes_list = notes_obj.get("Middle", [])
        for note_obj in middle_notes_list:
            note_name = note_obj.get("name")
            if note_name:
                heart_notes.append(note_name)
        
        # Extract base notes
        base_notes_list = notes_obj.get("Base", [])
        for note_obj in base_notes_list:
            note_name = note_obj.get("name")
            if note_name:
                base_notes.append(note_name)
    
    return Counter(top_notes), Counter(heart_notes), Counter(base_notes)

def extract_seasons_from_inventory():
    """
    Extract and count seasons from inventory.
    API returns "Season Ranking" as array of {name, score} objects.
    
    Returns:
        Counter: Counter object with season counts
    """
    seasons = []
    
    for perfume in st.session_state.user_inventory:
        season_ranking = perfume.get("Season Ranking", [])
        
        if season_ranking and len(season_ranking) > 0:
            # Take the best season (first in ranking)
            best_season = season_ranking[0].get("name", "")
            if best_season:
                seasons.append(best_season)
    
    return Counter(seasons)

def extract_occasions_from_inventory():
    """
    Extract and count occasions from inventory.
    API returns "Occasion Ranking" as array of {name, score} objects.
    
    Returns:
        Counter: Counter object with occasion counts
    """
    occasions = []
    
    for perfume in st.session_state.user_inventory:
        occasion_ranking = perfume.get("Occasion Ranking", [])
        
        if occasion_ranking and len(occasion_ranking) > 0:
            # Take the best occasion (first in ranking)
            best_occasion = occasion_ranking[0].get("name", "")
            if best_occasion:
                occasions.append(best_occasion)
    
    return Counter(occasions)

def search_perfume_to_add(query):
    """Search for perfumes to add to inventory."""
    if len(query) < 3:
        return []
    
    try:
        results = search_fragrances(query, limit=10)
        # Filter out perfumes already in inventory (use "Name" field)
        existing_names = [p.get("Name") for p in st.session_state.user_inventory]
        filtered = [p for p in results if p.get("Name") not in existing_names]
        return filtered
    except Exception as e:
        st.error(f"Error searching: {str(e)}")
        return []

# ============================================================================
# MAIN CONTENT - DETAIL VIEW
# ============================================================================

if st.session_state.selected_perfume is not None:
    perfume = st.session_state.selected_perfume
    
    # Back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back", key="back_to_inventory"):
            st.session_state.selected_perfume = None
            st.rerun()
    
    # Display detailed perfume information
    display_perfume_detail(perfume)
    
    # Remove from inventory button
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("🗑️ Remove from Collection", use_container_width=True, type="secondary"):
            # Remove perfume from inventory (use "Name" field)
            perfume_name = perfume.get("Name")
            st.session_state.user_inventory = [
                p for p in st.session_state.user_inventory 
                if p.get("Name") != perfume_name
            ]
            st.session_state.selected_perfume = None
            st.success("Removed from your collection!")
            st.rerun()

# ============================================================================
# MAIN CONTENT - INVENTORY VIEW
# ============================================================================

else:
    # Page title
    st.markdown('<div class="inventory-title">📚 My Perfume Collection</div>', unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("← Home"):
            st.switch_page("app.py")
    
    st.write("")
    
    # ========================================================================
    # COLLECTION STATISTICS
    # ========================================================================
    
    inventory = st.session_state.user_inventory
    
    if inventory:
        # Calculate statistics
        total_perfumes = len(inventory)
        
        # Extract unique brands (use "Brand" field)
        brands = set()
        for p in inventory:
            brand = p.get("Brand")
            if brand:
                brands.add(brand)
        total_brands = len(brands)
        
        # Extract unique accords (use "Main Accords" array)
        accords = set()
        for p in inventory:
            main_accords = p.get("Main Accords", [])
            for accord in main_accords:
                if accord:
                    accords.add(accord)
        total_accords = len(accords)
        
        # Display statistics cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{total_perfumes}</div>
                <div class="stat-label">Perfumes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{total_brands}</div>
                <div class="stat-label">Brands</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{total_accords}</div>
                <div class="stat-label">Unique Accords</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ====================================================================
        # NOTE COMPOSITION CHARTS
        # ====================================================================
        
        st.markdown('<div class="section-title">🎨 Note Composition</div>', unsafe_allow_html=True)
        
        # Extract notes
        top_notes, heart_notes, base_notes = extract_notes_from_inventory()
        
        # Create three donut charts
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        
        with chart_col1:
            if top_notes:
                fig = create_note_donut_chart(top_notes, "Top Notes", "#FFB6C1")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No top notes data available")
        
        with chart_col2:
            if heart_notes:
                fig = create_note_donut_chart(heart_notes, "Heart Notes", "#DDA0DD")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No heart notes data available")
        
        with chart_col3:
            if base_notes:
                fig = create_note_donut_chart(base_notes, "Base Notes", "#D8BFD8")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No base notes data available")
        
        # ====================================================================
        # SEASONALITY & OCCASION CHARTS
        # ====================================================================
        
        st.markdown('<div class="section-title">📊 Seasonality & Occasions</div>', unsafe_allow_html=True)
        
        chart_col1, chart_col2 = st.columns(2)
        
        # Seasonality chart
        with chart_col1:
            seasons = extract_seasons_from_inventory()
            if seasons:
                fig = create_bar_chart(
                    seasons,
                    "Best Seasons",
                    "Season",
                    "Count",
                    "#d4567b"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No seasonal data available")
        
        # Occasions chart
        with chart_col2:
            occasions = extract_occasions_from_inventory()
            if occasions:
                fig = create_bar_chart(
                    occasions,
                    "Best Occasions",
                    "Occasion",
                    "Count",
                    "#8b5a7c"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No occasion data available")
        
        # ====================================================================
        # PERFUME COLLECTION GRID
        # ====================================================================
        
        st.markdown('<div class="section-title">🌸 Your Perfumes</div>', unsafe_allow_html=True)
        
        # Add perfume button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("➕ Add New Perfume", use_container_width=True, type="primary"):
                st.session_state.show_add_perfume = not st.session_state.show_add_perfume
        
        st.write("")
        
        # Add perfume search interface
        if st.session_state.show_add_perfume:
            with st.container():
                st.markdown("### Search for a perfume to add")
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    search_query = st.text_input(
                        "Search perfumes",
                        value=st.session_state.add_search_query,
                        placeholder="Enter perfume name...",
                        key="add_perfume_search"
                    )
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("Search", key="add_search_btn"):
                        st.session_state.add_search_query = search_query
                        with st.spinner("Searching..."):
                            results = search_perfume_to_add(search_query)
                            st.session_state.add_search_results = results
                
                # Display search results
                if st.session_state.add_search_results:
                    st.write("")
                    st.markdown("**Select a perfume to add:**")
                    st.write("")
                    
                    for i, perfume in enumerate(st.session_state.add_search_results):
                        col1, col2, col3 = st.columns([1, 3, 1])
                        
                        with col1:
                            # Display perfume image (use "Image URL" field)
                            image_url = perfume.get("Image URL", "")
                            if image_url:
                                st.image(image_url, width=80)
                        
                        with col2:
                            # Use "Name" and "Brand" fields
                            st.markdown(f"**{perfume.get('Name', 'Unknown')}**")
                            st.markdown(f"*{perfume.get('Brand', 'Unknown Brand')}*")
                            
                            # Display main accords (use "Main Accords" array)
                            main_accords = perfume.get("Main Accords", [])
                            if main_accords:
                                accords_text = ", ".join(main_accords[:3])
                                st.caption(f"🎨 {accords_text}")
                        
                        with col3:
                            if st.button("Add", key=f"add_btn_{i}"):
                                st.session_state.user_inventory.append(perfume)
                                st.session_state.show_add_perfume = False
                                st.session_state.add_search_results = []
                                st.session_state.add_search_query = ""
                                st.success("Added to collection!")
                                st.rerun()
                        
                        st.markdown("---")
                
                st.write("")
                if st.button("Cancel", key="cancel_add"):
                    st.session_state.show_add_perfume = False
                    st.session_state.add_search_results = []
                    st.rerun()
        
        st.write("")
        
        # Display perfume collection in grid
        for i in range(0, len(inventory), 3):
            cols = st.columns(3)
            
            for j, col in enumerate(cols):
                if i + j < len(inventory):
                    perfume = inventory[i + j]
                    
                    with col:
                        # Display perfume card
                        display_perfume_card(perfume)
                        
                        # Action buttons
                        btn_col1, btn_col2 = st.columns(2)
                        
                        with btn_col1:
                            if st.button(
                                "View", 
                                key=f"inv_view_{i+j}",
                                use_container_width=True
                            ):
                                st.session_state.selected_perfume = perfume
                                st.rerun()
                        
                        with btn_col2:
                            if st.button(
                                "Remove",
                                key=f"inv_remove_{i+j}",
                                use_container_width=True,
                                type="secondary"
                            ):
                                # Use "Name" field
                                perfume_name = perfume.get("Name")
                                st.session_state.user_inventory = [
                                    p for p in st.session_state.user_inventory
                                    if p.get("Name") != perfume_name
                                ]
                                st.rerun()
            
            st.write("")
    
    # ========================================================================
    # EMPTY STATE
    # ========================================================================
    
    else:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📚</div>
            <h2 style="color: #d4567b;">Your collection is empty</h2>
            <p style="color: #8b5a7c; font-size: 1.1rem;">
                Start building your perfume collection by searching for fragrances 
                and adding them to your inventory.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            if st.button("🔍 Go to Search", use_container_width=True, type="primary"):
                st.switch_page("pages/01_Search.py")

