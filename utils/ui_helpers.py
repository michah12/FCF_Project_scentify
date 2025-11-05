"""
SCENTIFY - UI Helpers Module
Reusable UI components with CORRECT API field mappings

IMPORTANT: The Fragella API uses PascalCase with spaces:
- "Name", "Brand", "Image URL", "Main Accords", etc.

This module handles the display of perfume data with proper field access.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
from collections import Counter

# ============================================================================
# COLOR SCHEMES
# ============================================================================

# Accord color mapping for visual consistency
ACCORD_COLORS = {
    "floral": "#FFB6C1",
    "woody": "#8B4513",
    "citrus": "#FFD700",
    "fresh": "#87CEEB",
    "spicy": "#FF6347",
    "sweet": "#FF69B4",
    "fruity": "#FF8C00",
    "aromatic": "#9370DB",
    "aquatic": "#00CED1",
    "green": "#32CD32",
    "oriental": "#DAA520",
    "amber": "#FFBF00",
    "vanilla": "#F3E5AB",
    "leather": "#654321",
    "oud": "#5D3A1A",
    "musk": "#E0E0E0",
    "powdery": "#DDA0DD",
    "tobacco": "#8B4513",
    "gourmand": "#D2691E",
    "white floral": "#FFF0F5",
    "fresh spicy": "#FF7F50",
    "earthy": "#8B7355",
    "mossy": "#8FBC8F",
    "caramel": "#C68E17",
    "lactonic": "#FFF5EE"
}

# Default color for unknown accords
DEFAULT_ACCORD_COLOR = "#C8A2C8"

# ============================================================================
# IMAGE UTILITIES
# ============================================================================

def get_transparent_image_url(image_url: str) -> str:
    """
    Convert image URL to transparent background version.
    API returns "Image URL" field - change .jpg to .webp for transparency.
    
    Args:
        image_url (str): Original image URL from API
    
    Returns:
        str: Transparent version URL or original
    """
    if not image_url:
        return "https://via.placeholder.com/300x400.png?text=No+Image"
    
    # Replace .jpg with .webp for transparent background
    if image_url.endswith(".jpg"):
        return image_url.replace(".jpg", ".webp")
    
    return image_url

# ============================================================================
# ACCORD UTILITIES
# ============================================================================

def get_accord_color(accord_name: str) -> str:
    """
    Get color for an accord name.
    
    Args:
        accord_name (str): Name of the accord
    
    Returns:
        str: Hex color code
    """
    normalized = accord_name.lower().strip()
    return ACCORD_COLORS.get(normalized, DEFAULT_ACCORD_COLOR)

def format_accords(accords_list: List[str], max_count: int = 5) -> str:
    """
    Format list of accord strings as comma-separated string.
    API returns "Main Accords" as array of strings.
    
    Args:
        accords_list (list): List of accord name strings
        max_count (int): Maximum number to display
    
    Returns:
        str: Formatted accord string
    """
    if not accords_list:
        return "N/A"
    
    return ", ".join(accords_list[:max_count])

# ============================================================================
# PERFUME DISPLAY COMPONENTS
# ============================================================================

def display_perfume_card(perfume: Dict[str, Any]) -> None:
    """
    Display a perfume as a card with image, name, brand, and key info.
    
    API Fields Used (PascalCase with spaces):
    - Name: string
    - Brand: string
    - Image URL: string
    - Price: string
    - Main Accords: array of strings
    
    Args:
        perfume (dict): Perfume data from API
    """
    # Get perfume details using correct API field names
    name = perfume.get("Name", "Unknown Perfume")
    brand = perfume.get("Brand", "Unknown Brand")
    image_url = perfume.get("Image URL", "")
    price = perfume.get("Price", "")
    main_accords = perfume.get("Main Accords", [])
    
    # Display image
    transparent_url = get_transparent_image_url(image_url)
    try:
        st.image(transparent_url, use_container_width=True)
    except:
        st.image("https://via.placeholder.com/300x400.png?text=No+Image", use_container_width=True)
    
    # Display name and brand
    st.markdown(f"**{name}**")
    st.caption(brand)
    
    # Display price if available
    if price:
        st.caption(f"💰 ${price}")
    
    # Display main accords (first 3)
    if main_accords:
        accord_text = format_accords(main_accords, max_count=3)
        st.caption(f"🎨 {accord_text}")

def display_perfume_detail(perfume: Dict[str, Any]) -> None:
    """
    Display detailed perfume information with full layout.
    
    API Fields Used:
    - Name, Brand, Image URL, Price, Gender
    - Longevity, Sillage, OilType
    - General Notes: array of strings
    - Main Accords: array of strings
    - Main Accords Percentage: object {accord_name: "Dominant"/"Prominent"/etc.}
    - Notes: object with "Top", "Middle", "Base" arrays
    - Season Ranking: array of {name, score} objects
    - Occasion Ranking: array of {name, score} objects
    
    Args:
        perfume (dict): Perfume data from API
    """
    # Extract perfume details using correct API field names
    name = perfume.get("Name", "Unknown Perfume")
    brand = perfume.get("Brand", "Unknown Brand")
    image_url = perfume.get("Image URL", "")
    price = perfume.get("Price", "")
    gender = perfume.get("Gender", "Unisex")
    
    # Performance attributes
    longevity = perfume.get("Longevity", "N/A")
    sillage = perfume.get("Sillage", "N/A")
    oil_type = perfume.get("OilType", "")
    
    # Notes - API returns object with "Top", "Middle", "Base" keys
    notes_obj = perfume.get("Notes", {})
    top_notes = notes_obj.get("Top", [])
    middle_notes = notes_obj.get("Middle", [])
    base_notes = notes_obj.get("Base", [])
    
    # Accords
    main_accords = perfume.get("Main Accords", [])
    main_accords_percentage = perfume.get("Main Accords Percentage", {})
    
    # Rankings
    season_ranking = perfume.get("Season Ranking", [])
    occasion_ranking = perfume.get("Occasion Ranking", [])
    
    # General notes
    general_notes = perfume.get("General Notes", [])
    
    # ========================================================================
    # HEADER SECTION
    # ========================================================================
    
    st.markdown(f"# {name}")
    st.markdown(f"### *by {brand}*")
    
    st.write("")
    
    # ========================================================================
    # IMAGE AND KEY INFO
    # ========================================================================
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display image
        transparent_url = get_transparent_image_url(image_url)
        try:
            st.image(transparent_url, use_container_width=True)
        except:
            st.image("https://via.placeholder.com/300x400.png?text=No+Image", use_container_width=True)
    
    with col2:
        # Key information
        st.markdown("### Overview")
        
        if price:
            st.markdown(f"**💰 Price:** ${price}")
        
        st.markdown(f"**👤 Gender:** {gender.capitalize()}")
        
        if oil_type:
            st.markdown(f"**🧪 Type:** {oil_type}")
        
        if longevity != "N/A":
            st.markdown(f"**⏱️ Longevity:** {longevity}")
        
        if sillage != "N/A":
            st.markdown(f"**💨 Sillage:** {sillage}")
        
        st.write("")
        
        # General notes if available
        if general_notes:
            st.markdown("### Key Notes")
            st.write(", ".join(general_notes[:8]))
    
    st.write("")
    st.markdown("---")
    st.write("")
    
    # ========================================================================
    # NOTES SECTION
    # ========================================================================
    
    st.markdown("### 🌸 Fragrance Notes")
    st.write("")
    
    note_col1, note_col2, note_col3 = st.columns(3)
    
    with note_col1:
        st.markdown("**Top Notes**")
        if top_notes:
            for note_obj in top_notes[:6]:
                # Each note is an object with "name" and "imageUrl"
                note_name = note_obj.get("name", "Unknown")
                st.caption(f"• {note_name}")
        else:
            st.caption("No data")
    
    with note_col2:
        st.markdown("**Heart Notes**")
        if middle_notes:
            for note_obj in middle_notes[:6]:
                note_name = note_obj.get("name", "Unknown")
                st.caption(f"• {note_name}")
        else:
            st.caption("No data")
    
    with note_col3:
        st.markdown("**Base Notes**")
        if base_notes:
            for note_obj in base_notes[:6]:
                note_name = note_obj.get("name", "Unknown")
                st.caption(f"• {note_name}")
        else:
            st.caption("No data")
    
    st.write("")
    st.markdown("---")
    st.write("")
    
    # ========================================================================
    # ACCORDS SECTION
    # ========================================================================
    
    st.markdown("### 🎨 Main Accords")
    st.write("")
    
    if main_accords and main_accords_percentage:
        # Display accords with strength from Main Accords Percentage
        for accord in main_accords[:10]:  # Show top 10
            # Get strength descriptor from Main Accords Percentage object
            strength = main_accords_percentage.get(accord, "Moderate")
            
            # Get color for accord
            color = get_accord_color(accord)
            
            # Map strength to progress bar value (0-100)
            strength_values = {
                "Dominant": 100,
                "Prominent": 80,
                "Moderate": 60,
                "Subtle": 40,
                "Trace": 20
            }
            
            strength_value = strength_values.get(strength, 50)
            
            # Display accord name and strength
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**{accord.capitalize()}**")
            
            with col2:
                st.progress(strength_value / 100, text=strength)
    else:
        st.info("No accord data available")
    
    st.write("")
    st.markdown("---")
    st.write("")
    
    # ========================================================================
    # SEASONS AND OCCASIONS
    # ========================================================================
    
    attr_col1, attr_col2 = st.columns(2)
    
    with attr_col1:
        st.markdown("### 🌞 Best Seasons")
        if season_ranking:
            # Season Ranking is array of {name, score} objects, ordered best to worst
            for season_obj in season_ranking:
                season_name = season_obj.get("name", "").capitalize()
                score = season_obj.get("score", 0)
                st.caption(f"• {season_name} ({score:.2f})")
        else:
            st.caption("No data")
    
    with attr_col2:
        st.markdown("### 🎭 Best Occasions")
        if occasion_ranking:
            # Occasion Ranking is array of {name, score} objects, ordered best to worst
            for occasion_obj in occasion_ranking:
                occasion_name = occasion_obj.get("name", "").capitalize()
                score = occasion_obj.get("score", 0)
                st.caption(f"• {occasion_name} ({score:.2f})")
        else:
            st.caption("No data")

# ============================================================================
# CHART CREATION FUNCTIONS
# ============================================================================

def create_note_donut_chart(
    notes_counter: Counter,
    title: str,
    color: str = "#d4567b"
) -> go.Figure:
    """
    Create a donut chart for note composition.
    
    Args:
        notes_counter (Counter): Counter object with note counts
        title (str): Chart title
        color (str): Base color for chart
    
    Returns:
        plotly.graph_objects.Figure: Donut chart
    """
    # Get top 8 notes
    top_notes = notes_counter.most_common(8)
    
    if not top_notes:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No data",
            showarrow=False,
            font=dict(size=14, color="#999")
        )
        fig.update_layout(
            title=title,
            showlegend=False,
            height=300
        )
        return fig
    
    # Extract labels and values
    labels = [note[0] for note in top_notes]
    values = [note[1] for note in top_notes]
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(
            colors=px.colors.sequential.RdPu,
            line=dict(color='white', width=2)
        ),
        textposition='auto',
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color="#d4567b", family="Arial")
        ),
        showlegend=False,
        height=350,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_bar_chart(
    counter: Counter,
    title: str,
    xaxis_title: str,
    yaxis_title: str,
    color: str = "#d4567b"
) -> go.Figure:
    """
    Create a bar chart for categorical data.
    
    Args:
        counter (Counter): Counter object with category counts
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label
        color (str): Bar color
    
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    if not counter:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No data",
            showarrow=False,
            font=dict(size=14, color="#999")
        )
        fig.update_layout(
            title=title,
            showlegend=False,
            height=300
        )
        return fig
    
    # Sort by count (descending)
    sorted_items = counter.most_common()
    
    # Extract categories and counts
    categories = [item[0].capitalize() for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=counts,
        marker=dict(
            color=color,
            line=dict(color='white', width=1.5)
        ),
        text=counts,
        textposition='auto'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color="#d4567b", family="Arial")
        ),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        showlegend=False,
        height=350,
        margin=dict(t=50, b=50, l=50, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True
        )
    )
    
    return fig

