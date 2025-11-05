"""
SCENTIFY - Questionnaire Page
Personalized perfume recommendations based on user preferences

This page features:
- Five interactive sliders to capture user preferences
- Mapping of preferences to fragrance accords
- AI-powered recommendations using Fragella API
- Same detail view as Search page
- ML-based ranking of results
"""

import streamlit as st
from utils.api_client import match_fragrances
from utils.ui_helpers import display_perfume_card, display_perfume_detail
from utils.recommender import update_user_profile, rank_results

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Questionnaire - SCENTIFY",
    page_icon="📋",
    layout="wide"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []

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
    
    .quiz-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #d4567b;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .quiz-subtitle {
        font-size: 1.2rem;
        color: #8b5a7c;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .quiz-section {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .slider-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #d4567b;
        margin-bottom: 0.5rem;
    }
    
    .slider-description {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def map_preferences_to_accords(intensity, warmth, sweetness, occasion, gender_pref):
    """
    Map slider values to fragrance accords for API matching.
    
    Args:
        intensity (int): 1-5, where 1=Subtle, 5=Bold
        warmth (int): 1-5, where 1=Fresh/Light, 5=Warm/Intense
        sweetness (int): 1-5, where 1=Dry/Herbal, 5=Sweet/Gourmand
        occasion (int): 1-5, where 1=Daily/Office, 5=Evening/Event/Date
        gender_pref (int): 1-5, where 1=Feminine, 5=Masculine
    
    Returns:
        list: List of accord names to search for
    """
    accords = []
    
    # Map warmth preference
    if warmth <= 2:
        # Fresh/Light preferences
        accords.extend(["Citrus", "Aquatic", "Fresh", "Green"])
    elif warmth >= 4:
        # Warm/Intense preferences
        accords.extend(["Amber", "Spicy", "Oriental", "Woody"])
    else:
        # Moderate - add both
        accords.extend(["Aromatic", "Floral"])
    
    # Map sweetness preference
    if sweetness <= 2:
        # Dry/Herbal preferences
        accords.extend(["Woody", "Aromatic", "Green", "Leather"])
    elif sweetness >= 4:
        # Sweet/Gourmand preferences
        accords.extend(["Vanilla", "Sweet", "Fruity", "Gourmand"])
    else:
        # Moderate
        accords.extend(["Floral", "Powdery"])
    
    # Map intensity
    if intensity >= 4:
        # Bold - prefer strong accords
        accords.extend(["Spicy", "Oud", "Leather", "Tobacco"])
    else:
        # Subtle - prefer light accords
        accords.extend(["Musk", "Powdery", "Soft"])
    
    # Map occasion
    if occasion <= 2:
        # Daily/Office - fresh and professional
        accords.extend(["Fresh", "Clean", "Citrus"])
    elif occasion >= 4:
        # Evening/Event/Date - sophisticated and sensual
        accords.extend(["Oriental", "Amber", "Spicy", "Seductive"])
    
    # Map gender preference
    if gender_pref <= 2:
        # Feminine
        accords.extend(["Floral", "Powdery", "Fruity", "Sweet"])
    elif gender_pref >= 4:
        # Masculine
        accords.extend(["Woody", "Leather", "Aromatic", "Spicy"])
    # Unisex (middle range) - no specific additions
    
    # Remove duplicates and return
    return list(set(accords))

def get_recommendations(accords):
    """
    Get perfume recommendations from API based on accord preferences.
    
    Args:
        accords (list): List of accord names
    
    Returns:
        list: List of recommended perfumes
    """
    try:
        # Join accords with commas for API call
        accord_string = ",".join(accords[:5])  # Limit to top 5 accords
        
        # Call Fragella API match endpoint
        results = match_fragrances(accord_string)
        
        if not results:
            st.warning("No matches found. Try adjusting your preferences.")
            return []
        
        return results
        
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
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
        if st.button("← Back", key="back_to_quiz_results"):
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
# MAIN CONTENT - QUESTIONNAIRE VIEW
# ============================================================================

else:
    # Page title
    st.markdown('<div class="quiz-title">📋 Perfume Questionnaire</div>', unsafe_allow_html=True)
    st.markdown('<div class="quiz-subtitle">Answer a few questions to find your perfect scent</div>', 
               unsafe_allow_html=True)
    
    # Back to home button
    if st.button("← Back to Home"):
        st.switch_page("app.py")
    
    st.write("")
    
    # ========================================================================
    # QUESTIONNAIRE FORM
    # ========================================================================
    
    with st.container():
        st.markdown('<div class="quiz-section">', unsafe_allow_html=True)
        
        # Question 1: Intensity
        st.markdown('<div class="slider-label">1. Fragrance Intensity</div>', unsafe_allow_html=True)
        st.markdown('<div class="slider-description">How bold do you want your fragrance to be?</div>', 
                   unsafe_allow_html=True)
        
        intensity = st.slider(
            "intensity_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Subtle and understated | 5 = Bold and powerful"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🌸 Subtle & Understated")
        with col2:
            st.caption("💥 Bold & Powerful", )
        
        st.write("")
        st.write("")
        
        # Question 2: Warmth
        st.markdown('<div class="slider-label">2. Temperature Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="slider-description">Do you prefer fresh or warm fragrances?</div>', 
                   unsafe_allow_html=True)
        
        warmth = st.slider(
            "warmth_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Fresh and light | 5 = Warm and intense"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("❄️ Fresh & Light")
        with col2:
            st.caption("🔥 Warm & Intense")
        
        st.write("")
        st.write("")
        
        # Question 3: Sweetness
        st.markdown('<div class="slider-label">3. Sweetness Level</div>', unsafe_allow_html=True)
        st.markdown('<div class="slider-description">How sweet should your fragrance be?</div>', 
                   unsafe_allow_html=True)
        
        sweetness = st.slider(
            "sweetness_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Dry and herbal | 5 = Sweet and gourmand"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🌿 Dry & Herbal")
        with col2:
            st.caption("🍰 Sweet & Gourmand")
        
        st.write("")
        st.write("")
        
        # Question 4: Occasion
        st.markdown('<div class="slider-label">4. Primary Occasion</div>', unsafe_allow_html=True)
        st.markdown('<div class="slider-description">When will you wear this fragrance most?</div>', 
                   unsafe_allow_html=True)
        
        occasion = st.slider(
            "occasion_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Daily/Office wear | 5 = Evening/Special events"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("☀️ Daily & Office")
        with col2:
            st.caption("🌙 Evening & Events")
        
        st.write("")
        st.write("")
        
        # Question 5: Gender Preference
        st.markdown('<div class="slider-label">5. Style Preference</div>', unsafe_allow_html=True)
        st.markdown('<div class="slider-description">What style resonates with you?</div>', 
                   unsafe_allow_html=True)
        
        gender_pref = st.slider(
            "gender_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Feminine | 3 = Unisex | 5 = Masculine"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("💐 Feminine")
        with col2:
            st.caption("⚖️ Unisex")
        with col3:
            st.caption("🏔️ Masculine")
        
        st.write("")
        st.write("")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SUBMIT BUTTON
    # ========================================================================
    
    st.write("")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        submit_button = st.button(
            "Get Recommendations",
            use_container_width=True,
            type="primary"
        )
    
    # ========================================================================
    # PROCESS QUESTIONNAIRE & SHOW RESULTS
    # ========================================================================
    
    if submit_button:
        # Map preferences to accords
        accords = map_preferences_to_accords(
            intensity, warmth, sweetness, occasion, gender_pref
        )
        
        # Show selected accords
        st.write("")
        st.info(f"🎯 **Based on your preferences, we're looking for:** {', '.join(accords[:8])}")
        
        # Get recommendations
        with st.spinner("Finding your perfect matches..."):
            results = get_recommendations(accords)
            
            # Rank results using ML recommender if user has click history
            if st.session_state.clicked_perfumes:
                results = rank_results(results)
            
            st.session_state.quiz_results = results
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    if st.session_state.quiz_results:
        st.write("")
        st.write("")
        st.markdown("---")
        st.markdown(f"### 🌸 Your Personalized Recommendations ({len(st.session_state.quiz_results)} matches)")
        st.write("")
        
        results = st.session_state.quiz_results
        
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
                            key=f"quiz_view_{i+j}_{perfume.get('name', '')}",
                            use_container_width=True
                        ):
                            # Track click for ML recommendations
                            track_perfume_click(perfume)
                            
                            # Set selected perfume and rerun to show detail view
                            st.session_state.selected_perfume = perfume
                            st.rerun()
            
            st.write("")

