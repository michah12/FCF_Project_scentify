"""
SCENTIFY - API Client Module
Wrapper for Fragella API interactions

This module handles all API requests to the Fragella fragrance database:
- Authentication using Streamlit secrets
- GET requests with proper headers
- Error handling and retries
- Response caching
- Rate limit handling
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
) -> Optional[Dict[str, Any]]:
    """
    Make GET request to Fragella API with error handling and retries.
    
    Args:
        endpoint (str): API endpoint (e.g., '/fragrances')
        params (dict, optional): Query parameters
        retries (int): Number of retry attempts
    
    Returns:
        dict or None: JSON response data or None if request fails
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
                try:
                    data = response.json()
                    return data
                except ValueError as e:
                    st.error(f"Invalid JSON response: {str(e)}")
                    return None
            
            # Check for specific error codes
            elif response.status_code == 401:
                st.error("❌ Authentication failed. Please check your API key.")
                return None
            elif response.status_code == 403:
                st.error("❌ API key is invalid or incorrect.")
                return None
            elif response.status_code == 404:
                st.warning("⚠️ No results found.")
                return None
            
            # Other error codes
            else:
                error_msg = f"API returned status code: {response.status_code}"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "message" in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    pass
                st.warning(error_msg)
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
        
        except requests.exceptions.Timeout:
            st.warning(f"Request timeout. Attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None
        
        except requests.exceptions.ConnectionError:
            st.warning(f"Connection error. Attempt {attempt + 1}/{retries}")
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
        dict: Usage data including requests_remaining
        Example: {"requests_remaining": 950, "reset_time": "..."}
    """
    return make_request("/usage")

@st.cache_data(ttl=3600)
def search_fragrances(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search for fragrances by name, brand, or keyword.
    
    Endpoint: GET /fragrances?search=...
    
    Args:
        query (str): Search query string
        limit (int): Maximum number of results (default: 50)
    
    Returns:
        list: List of perfume dictionaries
        Each perfume contains: name, brand, image_url, description, main_accords, etc.
    """
    if not query or len(query) < 3:
        return []
    
    params = {
        "search": query,
        "limit": limit
    }
    
    result = make_request("/fragrances", params=params)
    
    # Handle different response formats
    if result:
        fragrances = []
        
        # Extract fragrances list from response
        if isinstance(result, list):
            fragrances = result
        elif isinstance(result, dict):
            if "fragrances" in result:
                fragrances = result["fragrances"]
            elif "data" in result:
                fragrances = result["data"]
            else:
                fragrances = [result]
        
        # Process each fragrance to ensure proper image URLs
        for fragrance in fragrances:
            if isinstance(fragrance, dict):
                # Convert main image URL to transparent if possible
                if "Image URL" in fragrance:
                    fragrance["Image URL"] = get_transparent_image(fragrance["Image URL"])
                elif "image_url" in fragrance:
                    fragrance["Image URL"] = get_transparent_image(fragrance["image_url"])
                    
                # Process note images
                if "Notes" in fragrance and isinstance(fragrance["Notes"], dict):
                    for note_type in ["Top", "Middle", "Base"]:
                        if note_type in fragrance["Notes"]:
                            for note in fragrance["Notes"][note_type]:
                                if "imageUrl" in note:
                                    note["imageUrl"] = get_transparent_image(note["imageUrl"])
        
        return fragrances[:limit]
    
    return []

@st.cache_data(ttl=3600)
def match_fragrances(accords: str, limit: int = 30) -> List[Dict[str, Any]]:
    """
    Find fragrances matching specific accords.
    
    Endpoint: GET /fragrances/match?accords=...
    
    Args:
        accords (str): Comma-separated list of accord names
                      Example: "Woody,Citrus,Fresh"
        limit (int): Maximum number of results
    
    Returns:
        list: List of matching perfume dictionaries
    """
    if not accords:
        return []
    
    params = {
        "accords": accords,
        "limit": limit
    }
    
    result = make_request("/fragrances/match", params=params)
    
    # Handle different response formats
    if result:
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "fragrances" in result:
            return result["fragrances"]
        elif isinstance(result, dict) and "data" in result:
            return result["data"]
        else:
            return [result]
    
    return []

@st.cache_data(ttl=3600)
def similar_fragrances(name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Find fragrances similar to a given perfume name.
    
    Endpoint: GET /fragrances/similar?name=...
    
    Args:
        name (str): Perfume name to find similar fragrances for
        limit (int): Maximum number of results
    
    Returns:
        list: List of similar perfume dictionaries
    """
    if not name:
        return []
    
    params = {
        "name": name,
        "limit": limit
    }
    
    result = make_request("/fragrances/similar", params=params)
    
    if result:
        if isinstance(result, dict) and "similar_fragrances" in result:
            return result["similar_fragrances"][:limit]
        elif isinstance(result, list):
            return result[:limit]
        elif isinstance(result, dict) and "fragrances" in result:
            return result["fragrances"][:limit]
        elif isinstance(result, dict) and "data" in result:
            return result["data"][:limit]
        else:
            return [result]
    
    return []

@st.cache_data(ttl=3600)
def brand_fragrances(brand_name: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get all fragrances from a specific brand.
    
    Endpoint: GET /brands/:brandName
    
    Args:
        brand_name (str): Name of the brand
        limit (int): Maximum number of results
    
    Returns:
        list: List of perfumes from the brand
    """
    if not brand_name:
        return []
    
    # Encode brand name for URL
    encoded_brand = brand_name.replace(" ", "%20")
    
    result = make_request(f"/brands/{encoded_brand}")
    
    if result:
        if isinstance(result, list):
            return result[:limit]
        elif isinstance(result, dict) and "fragrances" in result:
            return result["fragrances"][:limit]
        elif isinstance(result, dict) and "data" in result:
            return result["data"][:limit]
        else:
            return [result]
    
    return []

@st.cache_data(ttl=3600)
def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Search for perfume notes.
    
    Endpoint: GET /notes?search=...
    
    Args:
        query (str): Note search query
    
    Returns:
        list: List of note dictionaries
    """
    if not query:
        return []
    
    params = {"search": query}
    
    result = make_request("/notes", params=params)
    
    if result:
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "notes" in result:
            return result["notes"]
        elif isinstance(result, dict) and "data" in result:
            return result["data"]
        else:
            return [result]
    
    return []

@st.cache_data(ttl=3600)
def search_accords(query: str) -> List[Dict[str, Any]]:
    """
    Search for perfume accords.
    
    Endpoint: GET /accords?search=...
    
    Args:
        query (str): Accord search query
    
    Returns:
        list: List of accord dictionaries
    """
    if not query:
        return []
    
    params = {"search": query}
    
    result = make_request("/accords", params=params)
    
    if result:
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "accords" in result:
            return result["accords"]
        elif isinstance(result, dict) and "data" in result:
            return result["data"]
        else:
            return [result]
    
    return []

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_transparent_image(image_url: str) -> str:
    """
    Convert image URL to transparent background version if available.
    
    Fragella provides .webp versions with transparent backgrounds for .jpg images.
    This does not apply to fallback URLs.
    
    Args:
        image_url (str): Original image URL
    
    Returns:
        str: URL with transparent background or original URL
        Empty string if invalid or no URL provided
    """
    if not image_url:
        return ""
    
    try:
        # Check if URL is from Fragella CDN
        if "d2k6fvhyk5xgx.cloudfront.net" not in image_url:
            return image_url
            
        # Only convert main product images, not fallbacks
        if "/images/" not in image_url:
            return image_url
            
        # Try to replace .jpg with .webp for transparent background
        if image_url.lower().endswith(".jpg"):
            return image_url[:-4] + ".webp"
        
        return image_url
        
    except Exception as e:
        st.warning(f"Error processing image URL: {str(e)}")
        return image_url

