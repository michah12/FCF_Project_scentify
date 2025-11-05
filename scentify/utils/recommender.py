"""
SCENTIFY - ML Recommender Module
Content-based recommendation system using accord vectors

This module implements a lightweight machine learning recommender:
- Represents perfumes as weighted accord vectors
- Builds user profile from clicked perfumes
- Ranks new results using cosine similarity
- Considers click frequency for personalization
"""

import streamlit as st
import numpy as np
from typing import List, Dict, Any, Optional
from collections import defaultdict

# ============================================================================
# ACCORD STRENGTH WEIGHTS
# ============================================================================

# Mapping of accord strength labels to numeric weights
# These weights represent how dominant each accord is in the fragrance
ACCORD_WEIGHTS = {
    "dominant": 1.0,
    "prominent": 0.8,
    "moderate": 0.6,
    "subtle": 0.3,
    "trace": 0.1
}

# ============================================================================
# VECTOR REPRESENTATION FUNCTIONS
# ============================================================================

def perfume_to_vector(perfume: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert a perfume to a weighted accord vector.
    
    Args:
        perfume (dict): Perfume data dictionary with main_accords field
    
    Returns:
        dict: Accord name -> weight mapping
        Example: {"Woody": 1.0, "Citrus": 0.8, "Fresh": 0.6}
    """
    vector = {}
    
    # Extract main accords
    main_accords = perfume.get("main_accords", [])
    
    if not main_accords:
        return vector
    
    for accord in main_accords:
        # Get accord name
        accord_name = accord.get("name", "").lower()
        
        if not accord_name:
            continue
        
        # Get accord strength/prominence
        strength = accord.get("strength", "").lower()
        
        # If no strength field, check for prominence/intensity
        if not strength:
            strength = accord.get("prominence", "").lower()
        if not strength:
            strength = accord.get("intensity", "").lower()
        
        # Assign weight based on strength
        weight = ACCORD_WEIGHTS.get(strength, 0.5)  # Default 0.5 if unknown
        
        vector[accord_name] = weight
    
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
    # We need to find these perfumes in search results or inventory
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
        perfume_name = perfume.get("name", "")
        
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
    - Values closer to 1.0 indicate higher similarity
    
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
        perfume (dict): Perfume data dictionary
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

def get_recommended_perfumes(
    all_perfumes: List[Dict[str, Any]],
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Get top N recommended perfumes based on user profile.
    
    This is a convenience function that ranks perfumes and returns
    the top N results.
    
    Args:
        all_perfumes (list): List of all available perfumes
        top_n (int): Number of recommendations to return
    
    Returns:
        list: Top N recommended perfumes
    """
    # Rank all perfumes
    ranked = rank_results(all_perfumes)
    
    # Return top N
    return ranked[:top_n]

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

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

def get_diversity_score(perfumes: List[Dict[str, Any]]) -> float:
    """
    Calculate diversity score of a perfume collection.
    
    Higher score = more diverse collection of accords.
    Lower score = collection focuses on similar accords.
    
    Args:
        perfumes (list): List of perfumes
    
    Returns:
        float: Diversity score (0.0 to 1.0)
    """
    if not perfumes:
        return 0.0
    
    # Collect all unique accords
    all_accords = set()
    
    for perfume in perfumes:
        vector = perfume_to_vector(perfume)
        all_accords.update(vector.keys())
    
    # More unique accords = higher diversity
    # Normalize by a reasonable maximum (e.g., 20 unique accords)
    diversity = min(len(all_accords) / 20.0, 1.0)
    
    return diversity

def get_similarity_matrix(perfumes: List[Dict[str, Any]]) -> np.ndarray:
    """
    Calculate pairwise similarity matrix for a list of perfumes.
    
    Useful for finding similar perfumes within a collection.
    
    Args:
        perfumes (list): List of perfumes
    
    Returns:
        numpy.ndarray: NxN similarity matrix where N = len(perfumes)
    """
    n = len(perfumes)
    
    if n == 0:
        return np.array([])
    
    # Initialize matrix
    similarity_matrix = np.zeros((n, n))
    
    # Convert all perfumes to vectors
    vectors = [perfume_to_vector(p) for p in perfumes]
    
    # Calculate pairwise similarities
    for i in range(n):
        for j in range(i, n):
            if i == j:
                similarity_matrix[i][j] = 1.0
            else:
                sim = cosine_similarity(vectors[i], vectors[j])
                similarity_matrix[i][j] = sim
                similarity_matrix[j][i] = sim
    
    return similarity_matrix

