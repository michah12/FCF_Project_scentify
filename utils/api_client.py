"""
SCENTIFY - API Client Module
Wrapper for Fragella API interactions with CORRECT field mappings

This module handles all API requests to the Fragella fragrance database.
IMPORTANT: The API uses PascalCase field names with spaces (e.g., "Image URL", "Main Accords")
"""

import streamlit as st
import requests
import time
from typing import Optional, Dict, List, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

# Fragella API base URL
BASE_URL = "https://api.fragella.com/api/v1"

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Maximum number of retries for failed requests
MAX_RETRIES = 3

# Delay between retries (seconds)
RETRY_DELAY = 1

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_api_key() -> str:
    """
    Retrieve API key from Streamlit secrets.
    
    Returns:
        str: API key
    
    Raises:
        KeyError: If API key not found in secrets
    """
    try:
        return st.secrets["FRAGELLA_API_KEY"]
    except KeyError:
        st.error("❌ API key not found. Please configure FRAGELLA_API_KEY in Streamlit secrets.")
        raise

def get_headers() -> Dict[str, str]:
    """
    Build HTTP headers for API requests.
    
    Returns:
        dict: Headers dictionary with API key
    """
    api_key = get_api_key()
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def make_request(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    retries: int = MAX_RETRIES
) -> Optional[Any]:
    """
    Make GET request to Fragella API with error handling and retries.
    
    Args:
        endpoint (str): API endpoint (e.g., '/fragrances')
        params (dict, optional): Query parameters
        retries (int): Number of retry attempts
    
    Returns:
        Response data or None if request fails
    """
    url = f"{BASE_URL}{endpoint}"
    headers = get_headers()
    
    for attempt in range(retries):
        try:
            # Make GET request
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            
            # Check for rate limiting
            if response.status_code == 429:
                st.warning("⚠️ API rate limit reached. Please wait a moment.")
                time.sleep(RETRY_DELAY * 2)
                continue
            
            # Check for successful response
            if response.status_code == 200:
                return response.json()
            
            # Check for not found
            elif response.status_code == 404:
                return None
            
            # Other error codes
            else:
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
        
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None
        
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None
        
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    return None

# ============================================================================
# API ENDPOINT FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_usage() -> Optional[Dict[str, Any]]:
    """
    Get API usage statistics.
    
    Endpoint: GET /usage
    
    Returns:
        dict: Usage data with structure:
        {
            "plan": "free" or "pro",
            "billing_period": {"start": "...", "end": "..."},
            "limit": {
                "total_effective_limit": int,
                "base_limit": int,
                "carried_over_from_previous_period": int
            },
            "usage": {
                "requests_made": int,
                "requests_remaining": int
            }
        }
    """
    return make_request("/usage")

@st.cache_data(ttl=3600)
def search_fragrances(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for fragrances by name, brand, or keyword.
    
    Endpoint: GET /fragrances?search=...&limit=...
    
    API Response Fields (PascalCase with spaces):
    - Name: string
    - Brand: string
    - Image URL: string (can change .jpg to .webp for transparent)
    - Gender: string (women/men/unisex)
    - Price: string
    - Longevity: string (Poor/Weak/Moderate/Long Lasting/Very Long Lasting)
    - Sillage: string (Intimate/Soft/Moderate/Strong/Enormous)
    - OilType: string (Eau de Parfum, Eau de Toilette, etc.)
    - General Notes: array of strings
    - Main Accords: array of strings (ordered by prominence)
    - Main Accords Percentage: object mapping accord names to strength descriptors
    - Notes: object with Top, Middle, Base arrays
    - Season Ranking: array of {name, score} objects
    - Occasion Ranking: array of {name, score} objects
    - Image Fallbacks: optional array of strings
    - Purchase URL: optional string
    
    Args:
        query (str): Search query string (minimum 3 characters)
        limit (int): Maximum number of results (default: 10, max: 20)
    
    Returns:
        list: List of perfume dictionaries with API field names
    """
    if not query or len(query) < 3:
        return []
    
    params = {
        "search": query,
        "limit": min(limit, 20)  # API max is 20
    }
    
    result = make_request("/fragrances", params=params)
    
    # The API returns an array directly
    if isinstance(result, list):
        return result
    
    return []

@st.cache_data(ttl=3600)
def match_fragrances(accords: str = None, top: str = None, middle: str = None, 
                    base: str = None, general: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Find fragrances matching specific accords and notes.
    
    Endpoint: GET /fragrances/match?accords=...&top=...&middle=...&base=...&general=...&limit=...
    
    Args:
        accords (str): Comma-separated list of accord:minPercent
                      Example: "floral:90,fruity:80,citrus:70"
        top (str): Comma-separated list of required top notes
        middle (str): Comma-separated list of required middle notes
        base (str): Comma-separated list of required base notes
        general (str): Comma-separated list of notes that can appear anywhere
        limit (int): Maximum number of results (default: 10, max: 10)
    
    Returns:
        list: List of matching perfume dictionaries
    """
    params = {"limit": min(limit, 10)}  # API max is 10 for this endpoint
    
    if accords:
        params["accords"] = accords
    if top:
        params["top"] = top
    if middle:
        params["middle"] = middle
    if base:
        params["base"] = base
    if general:
        params["general"] = general
    
    # Need at least one parameter
    if len(params) == 1:  # Only limit
        return []
    
    result = make_request("/fragrances/match", params=params)
    
    if isinstance(result, list):
        return result
    
    return []

@st.cache_data(ttl=3600)
def similar_fragrances(name: str, limit: int = 10) -> Optional[Dict[str, Any]]:
    """
    Find fragrances similar to a given perfume name.
    
    Endpoint: GET /fragrances/similar?name=...&limit=...
    
    Args:
        name (str): Perfume name to find similar fragrances for
        limit (int): Maximum number of results (default: 10, max: 10)
    
    Returns:
        dict: Response with structure:
        {
            "similar_to": "Full Perfume Name",
            "similar_fragrances": [
                {"Name": "...", "SimilarityScore": 0.85},
                ...
            ]
        }
    """
    if not name:
        return None
    
    params = {
        "name": name,
        "limit": min(limit, 10)  # API max is 10
    }
    
    result = make_request("/fragrances/similar", params=params)
    
    return result

@st.cache_data(ttl=3600)
def brand_fragrances(brand_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get all fragrances from a specific brand.
    
    Endpoint: GET /brands/:brandName?limit=...
    
    Args:
        brand_name (str): Name of the brand (case-insensitive)
        limit (int): Maximum number of results (default: 10, max: 50)
    
    Returns:
        list: List of perfumes from the brand
    """
    if not brand_name:
        return []
    
    # URL encode the brand name
    encoded_brand = requests.utils.quote(brand_name)
    
    params = {"limit": min(limit, 50)}  # API max is 50
    
    result = make_request(f"/brands/{encoded_brand}", params=params)
    
    if isinstance(result, list):
        return result
    
    return []

@st.cache_data(ttl=3600)
def search_notes(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for perfume notes.
    
    Endpoint: GET /notes?search=...&limit=...
    
    Response Fields:
    - name: string
    - occurence: integer (number of fragrances containing this note)
    - description: string
    - imageUrl: string
    
    Args:
        query (str): Note search query (minimum 2 characters)
        limit (int): Maximum number of results (default: 10, max: 20)
    
    Returns:
        list: List of note dictionaries
    """
    if not query or len(query) < 2:
        return []
    
    params = {
        "search": query,
        "limit": min(limit, 20)  # API max is 20
    }
    
    result = make_request("/notes", params=params)
    
    if isinstance(result, list):
        return result
    
    return []

@st.cache_data(ttl=3600)
def search_accords(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for perfume accords.
    
    Endpoint: GET /accords?search=...&limit=...
    
    Response Fields:
    - name: string
    - occurence: integer (number of fragrances featuring this accord)
    - description: string
    
    Args:
        query (str): Accord search query (minimum 2 characters)
        limit (int): Maximum number of results (default: 10, max: 20)
    
    Returns:
        list: List of accord dictionaries
    """
    if not query or len(query) < 2:
        return []
    
    params = {
        "search": query,
        "limit": min(limit, 20)  # API max is 20
    }
    
    result = make_request("/accords", params=params)
    
    if isinstance(result, list):
        return result
    
    return []

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_transparent_image(image_url: str) -> str:
    """
    Convert image URL to transparent background version.
    
    Per API docs: Change .jpg extension to .webp for transparent background.
    This does NOT apply to Image Fallbacks URLs.
    
    Args:
        image_url (str): Original image URL
    
    Returns:
        str: URL with transparent background or original URL
    """
    if not image_url:
        return ""
    
    # Replace .jpg with .webp for transparent background
    if image_url.endswith(".jpg"):
        return image_url.replace(".jpg", ".webp")
    
    return image_url

