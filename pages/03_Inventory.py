"""
SCENTIFY - Perfume Inventory Page
Manage personal collection with visual analytics

This page features:
- User's saved perfume collection
- Add new perfumes via search
- Visual analytics: note composition, seasonality, occasions
- Three donut charts for Top/Heart/Base notes
- Bar charts for seasonal and occasion preferences
- Detail view for each perfume
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from utils.api_client import search_fragrances
from utils.ui_helpers import display_perfume_card, display_perfume_detail, create_note_donut_chart, create_bar_chart
from utils.recommender import update_user_profile

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
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_notes_from_inventory():
    """
    Extract and count all notes from user's inventory.
    
    Returns:
        tuple: (top_notes_counter, heart_notes_counter, base_notes_counter)
    """
    top_notes = []
    heart_notes = []
    base_notes = []
    
    for perfume in st.session_state.user_inventory:
        # Extract top notes
        if "top_notes" in perfume and perfume["top_notes"]:
            top_notes.extend([note.get("name") for note in perfume["top_notes"] if note.get("name")])
        
        # Extract middle/heart notes
        if "middle_notes" in perfume and perfume["middle_notes"]:
            heart_notes.extend([note.get("name") for note in perfume["middle_notes"] if note.get("name")])
        
        # Extract base notes
        if "base_notes" in perfume and perfume["base_notes"]:
            base_notes.extend([note.get("name") for note in perfume["base_notes"] if note.get("name")])
    
    return Counter(top_notes), Counter(heart_notes), Counter(base_notes)

def extract_attributes_from_inventory(attribute_key):
    """
    Extract and count specific attributes (seasons, occasions) from inventory.
    
    Args:
        attribute_key (str): Key to extract (e.g., 'seasons', 'occasions')
    
    Returns:
        Counter: Counter object with attribute counts
    """
    attributes = []
    
    for perfume in st.session_state.user_inventory:
        if attribute_key in perfume and perfume[attribute_key]:
            if isinstance(perfume[attribute_key], list):
                attributes.extend(perfume[attribute_key])
            elif isinstance(perfume[attribute_key], str):
                # Split by comma if it's a comma-separated string
                attributes.extend([s.strip() for s in perfume[attribute_key].split(",")])
    
    return Counter(attributes)

def search_perfume_to_add(query):
    """
    Search for perfumes to add to inventory.
    
    Args:
        query (str): Search query
    
    Returns:
        list: List of perfume results
    """
    if len(query) < 3:
        return []
    
    try:
        results = search_fragrances(query)
        # Filter out perfumes already in inventory
        existing_names = [p.get("name") for p in st.session_state.user_inventory]
        filtered = [p for p in results if p.get("name") not in existing_names]
        return filtered[:10]  # Limit to 10 results
    except Exception as e:
        st.error(f"Error searching: {str(e)}")
        return []

# ============================================================================
# MAIN CONTENT - DETAIL VIEW
# ============================================================================

# If a perfume is selected, show detail view
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
            # Remove perfume from inventory
            perfume_name = perfume.get("name")
            st.session_state.user_inventory = [
                p for p in st.session_state.user_inventory 
                if p.get("name") != perfume_name
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
        
        # Extract unique brands
        brands = set()
        for p in inventory:
            if p.get("brand"):
                brands.add(p.get("brand"))
        total_brands = len(brands)
        
        # Extract unique accords
        accords = set()
        for p in inventory:
            if p.get("main_accords"):
                for accord in p["main_accords"]:
                    if accord.get("name"):
                        accords.add(accord.get("name"))
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
            seasons = extract_attributes_from_inventory("seasons")
            if seasons:
                fig = create_bar_chart(
                    seasons,
                    "Seasonal Preferences",
                    "Season",
                    "Count",
                    "#d4567b"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No seasonal data available")
        
        # Occasions chart
        with chart_col2:
            occasions = extract_attributes_from_inventory("occasions")
            if occasions:
                fig = create_bar_chart(
                    occasions,
                    "Occasion Preferences",
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
                            # Display perfume image
                            if perfume.get("image_url"):
                                st.image(perfume["image_url"], width=80)
                        
                        with col2:
                            st.markdown(f"**{perfume.get('name', 'Unknown')}**")
                            st.markdown(f"*{perfume.get('brand', 'Unknown Brand')}*")
                            
                            # Display main accords
                            if perfume.get("main_accords"):
                                accords_text = ", ".join([
                                    a.get("name", "") for a in perfume["main_accords"][:3]
                                ])
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
                                perfume_name = perfume.get("name")
                                st.session_state.user_inventory = [
                                    p for p in st.session_state.user_inventory
                                    if p.get("name") != perfume_name
                                ]
                                st.rerun()
            
            st.write("")
    
    # ========================================================================
    # EMPTY STATE
    # ========================================================================
    
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📚</div>
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

