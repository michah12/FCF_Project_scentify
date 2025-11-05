"""
SCENTIFY - Questionnaire Page
Personalized perfume recommendations based on user preferences

Uses API: GET /fragrances/match with accord matching
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def map_preferences_to_accords(intensity, warmth, sweetness, occasion, gender_pref):
    """
    Map slider values to fragrance accords for API matching.
    Returns accord:minPercent pairs for API /fragrances/match endpoint.
    
    Args:
        intensity (int): 1-5, where 1=Subtle, 5=Bold
        warmth (int): 1-5, where 1=Fresh/Light, 5=Warm/Intense
        sweetness (int): 1-5, where 1=Dry/Herbal, 5=Sweet/Gourmand
        occasion (int): 1-5, where 1=Daily/Office, 5=Evening/Event
        gender_pref (int): 1-5, where 1=Feminine, 5=Masculine
    
    Returns:
        dict: Dictionary with 'accords_string' for API and 'accord_list' for display
    """
    # We'll build accord:percentage pairs
    accord_requirements = []
    
    # Map warmth preference
    if warmth <= 2:
        # Fresh/Light - require fresh/citrus/aquatic
        accord_requirements.append(("fresh", 70))
        accord_requirements.append(("citrus", 60))
    elif warmth >= 4:
        # Warm/Intense - require amber/spicy/oriental
        accord_requirements.append(("amber", 70))
        accord_requirements.append(("spicy", 60))
    else:
        # Moderate - floral/aromatic
        accord_requirements.append(("floral", 60))
    
    # Map sweetness preference
    if sweetness <= 2:
        # Dry/Herbal - require woody/aromatic
        accord_requirements.append(("woody", 60))
        accord_requirements.append(("aromatic", 50))
    elif sweetness >= 4:
        # Sweet/Gourmand - require sweet/vanilla/fruity
        accord_requirements.append(("sweet", 70))
        accord_requirements.append(("vanilla", 50))
    
    # Map gender preference
    if gender_pref <= 2:
        # Feminine - prefer floral
        accord_requirements.append(("floral", 60))
    elif gender_pref >= 4:
        # Masculine - prefer woody
        accord_requirements.append(("woody", 60))
    
    # Build API string: "accord1:percent1,accord2:percent2,..."
    accords_string = ",".join([f"{accord}:{percent}" for accord, percent in accord_requirements])
    
    # Extract just accord names for display
    accord_list = [accord for accord, _ in accord_requirements]
    
    return {
        "accords_string": accords_string,
        "accord_list": accord_list
    }

def track_perfume_click(perfume):
    """Track perfume click for ML recommendations."""
    perfume_name = perfume.get("Name", "Unknown")
    
    if perfume_name in st.session_state.clicked_perfumes:
        st.session_state.clicked_perfumes[perfume_name] += 1
    else:
        st.session_state.clicked_perfumes[perfume_name] = 1
    
    update_user_profile(perfume)

# ============================================================================
# MAIN CONTENT - DETAIL VIEW
# ============================================================================

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
        perfume_name = perfume.get("Name", "")
        is_in_inventory = any(p.get("Name") == perfume_name for p in st.session_state.user_inventory)
        
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
        st.markdown("---")
        
        # Question 1: Intensity
        st.markdown("#### 1️⃣ Fragrance Intensity")
        st.caption("How bold do you want your fragrance to be?")
        
        intensity = st.slider(
            "intensity_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Subtle | 5 = Bold"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🌸 Subtle & Understated")
        with col2:
            st.caption("💥 Bold & Powerful")
        
        st.write("")
        st.markdown("---")
        
        # Question 2: Warmth
        st.markdown("#### 2️⃣ Temperature Profile")
        st.caption("Do you prefer fresh or warm fragrances?")
        
        warmth = st.slider(
            "warmth_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Fresh/Light | 5 = Warm/Intense"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("❄️ Fresh & Light")
        with col2:
            st.caption("🔥 Warm & Intense")
        
        st.write("")
        st.markdown("---")
        
        # Question 3: Sweetness
        st.markdown("#### 3️⃣ Sweetness Level")
        st.caption("How sweet should your fragrance be?")
        
        sweetness = st.slider(
            "sweetness_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Dry/Herbal | 5 = Sweet/Gourmand"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🌿 Dry & Herbal")
        with col2:
            st.caption("🍰 Sweet & Gourmand")
        
        st.write("")
        st.markdown("---")
        
        # Question 4: Occasion
        st.markdown("#### 4️⃣ Primary Occasion")
        st.caption("When will you wear this fragrance most?")
        
        occasion = st.slider(
            "occasion_slider",
            min_value=1,
            max_value=5,
            value=3,
            format="%d",
            label_visibility="collapsed",
            help="1 = Daily/Office | 5 = Evening/Events"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("☀️ Daily & Office")
        with col2:
            st.caption("🌙 Evening & Events")
        
        st.write("")
        st.markdown("---")
        
        # Question 5: Gender Preference
        st.markdown("#### 5️⃣ Style Preference")
        st.caption("What style resonates with you?")
        
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
        st.markdown("---")
    
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
        accord_mapping = map_preferences_to_accords(
            intensity, warmth, sweetness, occasion, gender_pref
        )
        
        accords_string = accord_mapping["accords_string"]
        accord_list = accord_mapping["accord_list"]
        
        # Show selected accords
        st.write("")
        st.info(f"🎯 **Searching for:** {', '.join(set(accord_list))}")
        
        # Get recommendations from API
        with st.spinner("Finding your perfect matches..."):
            results = match_fragrances(accords=accords_string, limit=10)
            
            # Rank results using ML recommender if user has click history
            if st.session_state.clicked_perfumes and results:
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
                        perfume_name = perfume.get("Name", f"perfume_{i+j}")
                        if st.button(
                            "View Details",
                            key=f"quiz_view_{i+j}_{perfume_name}",
                            use_container_width=True
                        ):
                            # Track click
                            track_perfume_click(perfume)
                            
                            # Set selected perfume
                            st.session_state.selected_perfume = perfume
                            st.rerun()
            
            st.write("")

