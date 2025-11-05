"""
SCENTIFY - ML Recommender Module
Content-based recommendation system using accord vectors

IMPORTANT: Works with correct API field names:
- "Main Accords": array of strings (ordered by prominence)
- "Main Accords Percentage": object mapping accord names to strength descriptors
"""

import streamlit as st
import numpy as np
from typing import List, Dict, Any, Optional
from collections import defaultdict

# ============================================================================
# ACCORD STRENGTH WEIGHTS
# ============================================================================

# Mapping of API strength descriptors to numeric weights
# These come from the "Main Accords Percentage" field
ACCORD_WEIGHTS = {
    "Dominant": 1.0,      # Most powerful and defining accord
    "Prominent": 0.8,     # Very strong, shapes character
    "Moderate": 0.6,      # Clearly detectable, forms body
    "Subtle": 0.3,        # Background accord
    "Trace": 0.1          # Very faint hint
}

# ============================================================================
# VECTOR REPRESENTATION FUNCTIONS
# ============================================================================

def perfume_to_vector(perfume: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert a perfume to a weighted accord vector.
    
    Uses API fields:
    - "Main Accords": array of strings (ordered list)
    - "Main Accords Percentage": object {accord_name: "Dominant"/"Prominent"/etc.}
    
    Args:
        perfume (dict): Perfume data from API
    
    Returns:
        dict: Accord name -> weight mapping
        Example: {"sweet": 1.0, "floral": 0.8, "fruity": 0.6}
    """
    vector = {}
    
    # Get Main Accords array and Main Accords Percentage object
    main_accords = perfume.get("Main Accords", [])
    main_accords_percentage = perfume.get("Main Accords Percentage", {})
    
    if not main_accords:
        return vector
    
    for accord in main_accords:
        # Normalize accord name (lowercase)
        accord_normalized = accord.lower().strip()
        
        # Get strength descriptor from Main Accords Percentage
        strength = main_accords_percentage.get(accord, "Moderate")
        
        # Map strength to numeric weight
        weight = ACCORD_WEIGHTS.get(strength, 0.5)  # Default 0.5 if unknown
        
        vector[accord_normalized] = weight
    
    return vector

def build_user_profile(clicked_perfumes: Dict[str, int]) -> Dict[str, float]:
    """
    Build a user profile vector from clicked perfumes.
    
    The profile is a weighted average of accord vectors from all clicked perfumes,
    with weights based on click frequency.
    
    Args:
        clicked_perfumes (dict): Perfume name -> click count mapping
    
    Returns:
        dict: User profile as accord name -> weight mapping
    """
    # Accumulate accord weights across all clicked perfumes
    accord_accumulator = defaultdict(float)
    total_clicks = sum(clicked_perfumes.values())
    
    if total_clicks == 0:
        return {}
    
    # Get clicked perfume data from session state
    all_perfumes = []
    
    # Collect from search results
    if "search_results" in st.session_state:
        all_perfumes.extend(st.session_state.search_results)
    
    # Collect from quiz results
    if "quiz_results" in st.session_state:
        all_perfumes.extend(st.session_state.quiz_results)
    
    # Collect from inventory
    if "user_inventory" in st.session_state:
        all_perfumes.extend(st.session_state.user_inventory)
    
    # Build profile from clicked perfumes
    for perfume in all_perfumes:
        # API field name is "Name" (PascalCase)
        perfume_name = perfume.get("Name", "")
        
        if perfume_name not in clicked_perfumes:
            continue
        
        # Get click count for this perfume
        click_count = clicked_perfumes[perfume_name]
        
        # Convert perfume to vector
        perfume_vector = perfume_to_vector(perfume)
        
        # Add weighted accords to accumulator
        for accord, weight in perfume_vector.items():
            # Weight by click frequency
            accord_accumulator[accord] += weight * click_count
    
    # Normalize by total clicks to get average
    user_profile = {
        accord: weight / total_clicks
        for accord, weight in accord_accumulator.items()
    }
    
    return user_profile

def cosine_similarity(vector1: Dict[str, float], vector2: Dict[str, float]) -> float:
    """
    Calculate cosine similarity between two accord vectors.
    
    Cosine similarity measures the angle between two vectors:
    - 1.0 = identical direction (perfect match)
    - 0.0 = orthogonal (no similarity)
    
    Args:
        vector1 (dict): First accord vector
        vector2 (dict): Second accord vector
    
    Returns:
        float: Cosine similarity score (0.0 to 1.0)
    """
    # Get all unique accords
    all_accords = set(vector1.keys()) | set(vector2.keys())
    
    if not all_accords:
        return 0.0
    
    # Build numpy arrays for both vectors
    v1 = np.array([vector1.get(accord, 0.0) for accord in all_accords])
    v2 = np.array([vector2.get(accord, 0.0) for accord in all_accords])
    
    # Calculate dot product
    dot_product = np.dot(v1, v2)
    
    # Calculate magnitudes
    magnitude1 = np.linalg.norm(v1)
    magnitude2 = np.linalg.norm(v2)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    
    return float(similarity)

# ============================================================================
# RECOMMENDATION FUNCTIONS
# ============================================================================

def update_user_profile(perfume: Dict[str, Any]) -> None:
    """
    Update the user profile in session state based on a clicked perfume.
    
    This is called whenever a user clicks on a perfume to view details.
    
    Args:
        perfume (dict): Perfume data from API
    """
    # Get current clicked perfumes from session state
    clicked_perfumes = st.session_state.get("clicked_perfumes", {})
    
    # Build/update user profile
    user_profile = build_user_profile(clicked_perfumes)
    
    # Store in session state
    st.session_state.user_profile = user_profile

def rank_results(perfumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank perfume results based on user profile similarity.
    
    Uses cosine similarity to compare each perfume's accord vector
    with the user's preference profile built from click history.
    
    Args:
        perfumes (list): List of perfume dictionaries to rank
    
    Returns:
        list: Sorted list of perfumes (highest similarity first)
    """
    # Get user profile from session state
    user_profile = st.session_state.get("user_profile")
    
    # If no user profile exists, return results as-is
    if not user_profile:
        return perfumes
    
    # Calculate similarity scores for each perfume
    scored_perfumes = []
    
    for perfume in perfumes:
        # Convert perfume to vector
        perfume_vector = perfume_to_vector(perfume)
        
        # Calculate similarity to user profile
        similarity = cosine_similarity(user_profile, perfume_vector)
        
        # Add similarity score to perfume data
        perfume_copy = perfume.copy()
        perfume_copy["_similarity_score"] = similarity
        
        scored_perfumes.append(perfume_copy)
    
    # Sort by similarity score (descending)
    ranked_perfumes = sorted(
        scored_perfumes,
        key=lambda p: p.get("_similarity_score", 0.0),
        reverse=True
    )
    
    return ranked_perfumes

def get_user_accord_preferences() -> Dict[str, float]:
    """
    Get the user's accord preferences from their profile.
    
    Returns:
        dict: Accord name -> preference weight, sorted by weight
    """
    user_profile = st.session_state.get("user_profile", {})
    
    # Sort by weight (descending)
    sorted_accords = dict(
        sorted(user_profile.items(), key=lambda x: x[1], reverse=True)
    )
    
    return sorted_accords

