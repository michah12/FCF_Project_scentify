"""
SCENTIFY - UI Helpers Module
Reusable UI components and utility functions

This module provides:
- Perfume card display component
- Detailed perfume view component
- Chart creation functions (Plotly)
- Accord color mapping
- Image URL utilities
- Layout helpers
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
    "gourmand": "#D2691E"
}

# Default color for unknown accords
DEFAULT_ACCORD_COLOR = "#C8A2C8"

# ============================================================================
# IMAGE UTILITIES
# ============================================================================

def get_transparent_image_url(image_url: str) -> str:
    """
    Convert image URL to transparent background version.
    
    Args:
        image_url (str): Original image URL
    
    Returns:
        str: Transparent version URL or original if not available
    """
    if not image_url:
        return ""
    
    # Try to replace .jpg with .webp for transparent background
    if image_url.endswith(".jpg"):
        return image_url.replace(".jpg", ".webp")
    
    return image_url

def get_fallback_image() -> str:
    """
    Get fallback image URL for perfumes without images.
    
    Returns:
        str: URL to placeholder image
    """
    # Simple placeholder - you can replace with a better one
    return "https://via.placeholder.com/300x400.png?text=No+Image"

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
    # Normalize accord name (lowercase, strip whitespace)
    normalized = accord_name.lower().strip()
    
    # Return matching color or default
    return ACCORD_COLORS.get(normalized, DEFAULT_ACCORD_COLOR)

def format_accords(accords: List[Dict[str, Any]], max_count: int = 5) -> str:
    """
    Format list of accords as comma-separated string.
    
    Args:
        accords (list): List of accord dictionaries
        max_count (int): Maximum number of accords to include
    
    Returns:
        str: Formatted accord string
    """
    if not accords:
        return "N/A"
    
    accord_names = [a.get("name", "") for a in accords[:max_count] if a.get("name")]
    
    return ", ".join(accord_names)

# ============================================================================
# PERFUME DISPLAY COMPONENTS
# ============================================================================

def display_perfume_card(perfume: Dict[str, Any]) -> None:
    """
    Display a perfume as a card with image, name, brand, and key info.
    
    Args:
        perfume (dict): Perfume data dictionary
    """
    # Get perfume details
    name = perfume.get("name", "Unknown Perfume")
    brand = perfume.get("brand", "Unknown Brand")
    image_url = perfume.get("image_url", "")
    price = perfume.get("price")
    main_accords = perfume.get("main_accords", [])
    
    # Display image
    if image_url:
        try:
            # Try transparent version first
            transparent_url = get_transparent_image_url(image_url)
            st.image(transparent_url, use_container_width=True)
        except:
            # Fallback to original or placeholder
            try:
                st.image(image_url, use_container_width=True)
            except:
                st.image(get_fallback_image(), use_container_width=True)
    else:
        st.image(get_fallback_image(), use_container_width=True)
    
    # Display name and brand
    st.markdown(f"**{name}**")
    st.caption(brand)
    
    # Display price if available
    if price:
        st.caption(f"💰 ${price}")
    
    # Display main accords
    if main_accords:
        accord_text = format_accords(main_accords, max_count=3)
        st.caption(f"🎨 {accord_text}")

def display_perfume_detail(perfume: Dict[str, Any]) -> None:
    """
    Display detailed perfume information with full layout.
    
    Args:
        perfume (dict): Perfume data dictionary with full details
    """
    # Extract perfume details
    name = perfume.get("name", "Unknown Perfume")
    brand = perfume.get("brand", "Unknown Brand")
    image_url = perfume.get("image_url", "")
    description = perfume.get("description", "No description available.")
    price = perfume.get("price")
    gender = perfume.get("gender", "Unisex")
    
    # Notes
    top_notes = perfume.get("top_notes", [])
    middle_notes = perfume.get("middle_notes", [])
    base_notes = perfume.get("base_notes", [])
    
    # Accords
    main_accords = perfume.get("main_accords", [])
    
    # Attributes
    seasons = perfume.get("seasons", [])
    occasions = perfume.get("occasions", [])
    longevity = perfume.get("longevity", "N/A")
    sillage = perfume.get("sillage", "N/A")
    
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
        if image_url:
            try:
                transparent_url = get_transparent_image_url(image_url)
                st.image(transparent_url, use_container_width=True)
            except:
                try:
                    st.image(image_url, use_container_width=True)
                except:
                    st.image(get_fallback_image(), use_container_width=True)
        else:
            st.image(get_fallback_image(), use_container_width=True)
    
    with col2:
        # Key information
        st.markdown("### Overview")
        
        if price:
            st.markdown(f"**💰 Price:** ${price}")
        
        st.markdown(f"**👤 Gender:** {gender}")
        
        if longevity != "N/A":
            st.markdown(f"**⏱️ Longevity:** {longevity}")
        
        if sillage != "N/A":
            st.markdown(f"**💨 Sillage:** {sillage}")
        
        st.write("")
        
        # Description
        st.markdown("### Description")
        st.write(description)
    
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
            for note in top_notes:
                st.caption(f"• {note.get('name', 'Unknown')}")
        else:
            st.caption("No data")
    
    with note_col2:
        st.markdown("**Heart Notes**")
        if middle_notes:
            for note in middle_notes:
                st.caption(f"• {note.get('name', 'Unknown')}")
        else:
            st.caption("No data")
    
    with note_col3:
        st.markdown("**Base Notes**")
        if base_notes:
            for note in base_notes:
                st.caption(f"• {note.get('name', 'Unknown')}")
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
    
    if main_accords:
        # Display accords with visual strength indicators
        for accord in main_accords:
            accord_name = accord.get("name", "Unknown")
            strength = accord.get("strength", "moderate")
            
            # Get color for accord
            color = get_accord_color(accord_name)
            
            # Map strength to progress bar value (0-100)
            strength_values = {
                "dominant": 100,
                "prominent": 80,
                "moderate": 60,
                "subtle": 40,
                "trace": 20
            }
            
            strength_value = strength_values.get(strength.lower(), 50)
            
            # Display accord name and strength
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**{accord_name}**")
            
            with col2:
                st.progress(strength_value / 100, text=strength.capitalize())
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
        if seasons:
            if isinstance(seasons, list):
                for season in seasons:
                    st.caption(f"• {season}")
            else:
                st.caption(f"• {seasons}")
        else:
            st.caption("No data")
    
    with attr_col2:
        st.markdown("### 🎭 Occasions")
        if occasions:
            if isinstance(occasions, list):
                for occasion in occasions:
                    st.caption(f"• {occasion}")
            else:
                st.caption(f"• {occasions}")
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
    categories = [item[0] for item in sorted_items]
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

# ============================================================================
# LAYOUT HELPERS
# ============================================================================

def create_chip(label: str, color: str = "#d4567b") -> str:
    """
    Create HTML for a colored chip/badge.
    
    Args:
        label (str): Chip text
        color (str): Background color
    
    Returns:
        str: HTML string for chip
    """
    return f"""
    <span style="
        display: inline-block;
        background-color: {color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.25rem;
        font-weight: 500;
    ">
        {label}
    </span>
    """

def display_chips(labels: List[str]) -> None:
    """
    Display a list of labels as colored chips.
    
    Args:
        labels (list): List of label strings
    """
    if not labels:
        return
    
    chips_html = ""
    for label in labels:
        # Get color based on label (if it's an accord)
        color = get_accord_color(label)
        chips_html += create_chip(label, color)
    
    st.markdown(chips_html, unsafe_allow_html=True)

