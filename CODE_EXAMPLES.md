# 🌸 SCENTIFY - Code Examples & Implementation Details

This document showcases key code snippets from the SCENTIFY application to demonstrate implementation quality and architecture.

---

## 🎯 Table of Contents

1. [API Integration](#api-integration)
2. [Machine Learning Recommender](#machine-learning-recommender)
3. [UI Components](#ui-components)
4. [Session State Management](#session-state-management)
5. [Data Visualization](#data-visualization)

---

## 🔌 API Integration

### API Client with Authentication

```python
# utils/api_client.py

def get_headers() -> Dict[str, str]:
    """Build HTTP headers for API requests with authentication."""
    api_key = st.secrets["FRAGELLA_API_KEY"]  # Never hardcoded!
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
```

### Error Handling & Retries

```python
def make_request(endpoint: str, params: Optional[Dict] = None, 
                 retries: int = MAX_RETRIES):
    """Make GET request with automatic retries and error handling."""
    url = f"{BASE_URL}{endpoint}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=get_headers(), 
                                   params=params, timeout=REQUEST_TIMEOUT)
            
            # Handle rate limiting
            if response.status_code == 429:
                st.warning("⚠️ API rate limit reached. Waiting...")
                time.sleep(RETRY_DELAY * 2)
                continue
            
            # Success
            if response.status_code == 200:
                return response.json()
        
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
    
    return None
```

### Cached API Calls

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def search_fragrances(query: str, limit: int = 50):
    """Search fragrances with caching to reduce API calls."""
    params = {"search": query, "limit": limit}
    result = make_request("/fragrances", params=params)
    
    # Handle different response formats
    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and "fragrances" in result:
        return result["fragrances"]
    
    return []
```

---

## 🤖 Machine Learning Recommender

### Perfume Vector Representation

```python
# utils/recommender.py

# Accord strength weights for vector representation
ACCORD_WEIGHTS = {
    "dominant": 1.0,
    "prominent": 0.8,
    "moderate": 0.6,
    "subtle": 0.3,
    "trace": 0.1
}

def perfume_to_vector(perfume: Dict) -> Dict[str, float]:
    """
    Convert perfume to weighted accord vector.
    
    Example output:
    {"woody": 1.0, "citrus": 0.8, "fresh": 0.6}
    """
    vector = {}
    
    for accord in perfume.get("main_accords", []):
        accord_name = accord.get("name", "").lower()
        strength = accord.get("strength", "").lower()
        weight = ACCORD_WEIGHTS.get(strength, 0.5)
        vector[accord_name] = weight
    
    return vector
```

### Cosine Similarity Calculation

```python
def cosine_similarity(vector1: Dict[str, float], 
                      vector2: Dict[str, float]) -> float:
    """
    Calculate cosine similarity between two accord vectors.
    Returns value from 0.0 (no similarity) to 1.0 (identical).
    """
    all_accords = set(vector1.keys()) | set(vector2.keys())
    
    v1 = np.array([vector1.get(accord, 0.0) for accord in all_accords])
    v2 = np.array([vector2.get(accord, 0.0) for accord in all_accords])
    
    dot_product = np.dot(v1, v2)
    magnitude1 = np.linalg.norm(v1)
    magnitude2 = np.linalg.norm(v2)
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return float(dot_product / (magnitude1 * magnitude2))
```

### User Profile Building

```python
def build_user_profile(clicked_perfumes: Dict[str, int]) -> Dict[str, float]:
    """
    Build user profile from clicked perfumes.
    
    Args:
        clicked_perfumes: {"Perfume Name": click_count, ...}
    
    Returns:
        User profile as accord vector
    """
    accord_accumulator = defaultdict(float)
    total_clicks = sum(clicked_perfumes.values())
    
    for perfume in all_perfumes:
        perfume_name = perfume.get("name")
        
        if perfume_name in clicked_perfumes:
            click_count = clicked_perfumes[perfume_name]
            perfume_vector = perfume_to_vector(perfume)
            
            for accord, weight in perfume_vector.items():
                # Weight by click frequency
                accord_accumulator[accord] += weight * click_count
    
    # Normalize by total clicks
    user_profile = {
        accord: weight / total_clicks
        for accord, weight in accord_accumulator.items()
    }
    
    return user_profile
```

### Personalized Ranking

```python
def rank_results(perfumes: List[Dict]) -> List[Dict]:
    """Rank perfumes by similarity to user profile."""
    user_profile = st.session_state.get("user_profile")
    
    if not user_profile:
        return perfumes  # No ranking without profile
    
    scored_perfumes = []
    for perfume in perfumes:
        perfume_vector = perfume_to_vector(perfume)
        similarity = cosine_similarity(user_profile, perfume_vector)
        
        perfume_copy = perfume.copy()
        perfume_copy["_similarity_score"] = similarity
        scored_perfumes.append(perfume_copy)
    
    # Sort by similarity (descending)
    return sorted(scored_perfumes, 
                 key=lambda p: p.get("_similarity_score", 0.0), 
                 reverse=True)
```

---

## 🎨 UI Components

### Perfume Card Display

```python
# utils/ui_helpers.py

def display_perfume_card(perfume: Dict[str, Any]) -> None:
    """Display perfume as a card with image and key info."""
    name = perfume.get("name", "Unknown Perfume")
    brand = perfume.get("brand", "Unknown Brand")
    image_url = get_transparent_image_url(perfume.get("image_url", ""))
    
    # Display image
    st.image(image_url, use_container_width=True)
    
    # Display details
    st.markdown(f"**{name}**")
    st.caption(brand)
    
    # Show price if available
    if perfume.get("price"):
        st.caption(f"💰 ${perfume['price']}")
    
    # Show main accords
    if perfume.get("main_accords"):
        accord_text = format_accords(perfume["main_accords"], max_count=3)
        st.caption(f"🎨 {accord_text}")
```

### Custom CSS Styling

```python
# app.py

st.markdown("""
<style>
    /* Floral-themed background */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #fff5f7 100%);
    }
    
    /* Navigation cards with hover effect */
    .nav-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(212, 86, 123, 0.2);
    }
</style>
""", unsafe_allow_html=True)
```

---

## 💾 Session State Management

### Initialization Pattern

```python
# app.py

# Initialize all session state variables
if "user_inventory" not in st.session_state:
    st.session_state.user_inventory = []

if "clicked_perfumes" not in st.session_state:
    st.session_state.clicked_perfumes = {}

if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
```

### Click Tracking

```python
# pages/01_Search.py

def track_perfume_click(perfume: Dict):
    """Track user clicks for ML recommendations."""
    perfume_name = perfume.get("name", "Unknown")
    
    # Increment click count
    if perfume_name in st.session_state.clicked_perfumes:
        st.session_state.clicked_perfumes[perfume_name] += 1
    else:
        st.session_state.clicked_perfumes[perfume_name] = 1
    
    # Update user profile
    update_user_profile(perfume)

# Usage in button click
if st.button("View Details", key=f"view_{perfume_name}"):
    track_perfume_click(perfume)
    st.session_state.selected_perfume = perfume
    st.rerun()
```

---

## 📊 Data Visualization

### Donut Chart Creation

```python
# utils/ui_helpers.py

def create_note_donut_chart(notes_counter: Counter, 
                           title: str, 
                           color: str) -> go.Figure:
    """Create interactive Plotly donut chart for note composition."""
    top_notes = notes_counter.most_common(8)
    labels = [note[0] for note in top_notes]
    values = [note[1] for note in top_notes]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Donut hole
        marker=dict(
            colors=px.colors.sequential.RdPu,
            line=dict(color='white', width=2)
        ),
        textposition='auto',
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent
    )
    
    return fig
```

### Bar Chart with Custom Styling

```python
def create_bar_chart(counter: Counter, 
                     title: str,
                     color: str = "#d4567b") -> go.Figure:
    """Create styled bar chart for categorical data."""
    sorted_items = counter.most_common()
    categories = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=counts,
        marker=dict(color=color),
        text=counts,
        textposition='auto'
    )])
    
    fig.update_layout(
        title=title,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(200,200,200,0.3)'),
        yaxis=dict(gridcolor='rgba(200,200,200,0.3)')
    )
    
    return fig
```

### Usage in Inventory Page

```python
# pages/03_Inventory.py

# Extract notes from user's collection
top_notes, heart_notes, base_notes = extract_notes_from_inventory()

# Create three donut charts
col1, col2, col3 = st.columns(3)

with col1:
    fig = create_note_donut_chart(top_notes, "Top Notes", "#FFB6C1")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = create_note_donut_chart(heart_notes, "Heart Notes", "#DDA0DD")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = create_note_donut_chart(base_notes, "Base Notes", "#D8BFD8")
    st.plotly_chart(fig, use_container_width=True)
```

---

## 🎯 Questionnaire Logic

### Preference Mapping

```python
# pages/02_Questionnaire.py

def map_preferences_to_accords(intensity, warmth, sweetness, 
                               occasion, gender_pref):
    """
    Map slider values (1-5) to fragrance accords.
    
    Returns list of accord names for API matching.
    """
    accords = []
    
    # Map warmth preference
    if warmth <= 2:  # Fresh/Light
        accords.extend(["Citrus", "Aquatic", "Fresh", "Green"])
    elif warmth >= 4:  # Warm/Intense
        accords.extend(["Amber", "Spicy", "Oriental", "Woody"])
    else:  # Moderate
        accords.extend(["Aromatic", "Floral"])
    
    # Map sweetness preference
    if sweetness <= 2:  # Dry/Herbal
        accords.extend(["Woody", "Aromatic", "Green", "Leather"])
    elif sweetness >= 4:  # Sweet/Gourmand
        accords.extend(["Vanilla", "Sweet", "Fruity", "Gourmand"])
    
    # ... additional mappings ...
    
    return list(set(accords))  # Remove duplicates
```

### Slider Interface

```python
# Interactive slider with labels
intensity = st.slider(
    "intensity_slider",
    min_value=1,
    max_value=5,
    value=3,
    help="1 = Subtle | 5 = Bold"
)

col1, col2 = st.columns(2)
with col1:
    st.caption("🌸 Subtle & Understated")
with col2:
    st.caption("💥 Bold & Powerful")
```

---

## 🔍 Advanced Search with Filters

```python
# pages/01_Search.py

def perform_search(query: str, filters: Dict = None):
    """Search with client-side filtering."""
    results = search_fragrances(query)
    
    if filters:
        # Filter by brand
        if filters.get("brand"):
            results = [p for p in results 
                      if p.get("brand", "").lower() == 
                         filters["brand"].lower()]
        
        # Filter by gender
        if filters.get("gender") and filters["gender"] != "All":
            results = [p for p in results 
                      if filters["gender"].lower() in 
                         p.get("gender", "").lower()]
        
        # Filter by price range
        if filters.get("price_range"):
            min_price, max_price = filters["price_range"]
            results = [p for p in results 
                      if min_price <= p.get("price", 0) <= max_price]
        
        # Filter by accords
        if filters.get("accords"):
            results = [p for p in results
                      if any(accord.lower() in 
                            [a.get("name", "").lower() 
                             for a in p.get("main_accords", [])]
                            for accord in filters["accords"])]
    
    return results
```

---

## 🎨 Accord Color Mapping

```python
# utils/ui_helpers.py

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
    # ... 19 total accords mapped
}

def get_accord_color(accord_name: str) -> str:
    """Get color for an accord with fallback."""
    normalized = accord_name.lower().strip()
    return ACCORD_COLORS.get(normalized, DEFAULT_ACCORD_COLOR)
```

---

## 📱 Responsive Layout

```python
# Three-column grid for perfume cards
for i in range(0, len(results), 3):
    cols = st.columns(3)
    
    for j, col in enumerate(cols):
        if i + j < len(results):
            perfume = results[i + j]
            
            with col:
                display_perfume_card(perfume)
                
                if st.button("View Details", key=f"view_{i+j}"):
                    st.session_state.selected_perfume = perfume
                    st.rerun()
```

---

## 🌟 Key Design Patterns

1. **Separation of Concerns**
   - API logic in `utils/api_client.py`
   - ML logic in `utils/recommender.py`
   - UI components in `utils/ui_helpers.py`

2. **Caching Strategy**
   - All API calls cached with `@st.cache_data`
   - 1-hour TTL to balance freshness and performance

3. **Error Handling**
   - Try-except blocks around all API calls
   - Graceful degradation to sample data
   - User-friendly error messages

4. **Session Persistence**
   - All user data in `st.session_state`
   - Persists across page navigations
   - Cleared on browser refresh

5. **Progressive Enhancement**
   - App works without API (uses sample data)
   - ML ranking optional (works without user profile)
   - Images have fallbacks

---

## 🚀 Performance Optimizations

1. **API Request Caching** - Reduces redundant calls
2. **Vector Calculations** - NumPy for fast computation
3. **Lazy Loading** - Charts only created when needed
4. **Efficient Filtering** - Client-side to reduce API load
5. **Minimal Re-renders** - Strategic use of `st.rerun()`

---

**This codebase demonstrates production-ready Streamlit development with clean architecture, comprehensive error handling, and intelligent ML integration! 🌸**

