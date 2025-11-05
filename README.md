# 🌸 SCENTIFY - Perfume Finder & Recommendation App

A beautiful, intelligent Streamlit web application for discovering and managing your perfect fragrances, powered by the **Fragella API** with **correct field mappings**.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## ✨ Features

### 🔍 **Search**
- Search perfumes by name, brand, or keyword (min 3 characters)
- Detailed perfume information with all API fields
- ML-powered personalized ranking based on your click history
- Add perfumes to your collection

### 📋 **Questionnaire**
- 5 interactive sliders for preference capture
- Maps preferences to fragrance accords
- Uses API `/fragrances/match` endpoint for intelligent matching
- Personalized results with ML ranking

### 📚 **Perfume Inventory**
- Build your personal fragrance collection
- Visual analytics with interactive charts:
  - Note composition (Top, Heart, Base notes)
  - Seasonal preferences
  - Occasion breakdown
- Collection statistics

### 🤖 **Machine Learning**
- Content-based recommender using accord vectors
- Learns from your clicks and preferences
- Cosine similarity ranking for personalized results

---

## 🚀 Deployment to Streamlit Cloud

### **Step 1: Push to GitHub**

```bash
cd /Users/michahansli/Desktop/HSG
git init
git add .
git commit -m "Initial commit: SCENTIFY perfume app"
git remote add origin https://github.com/YOUR_USERNAME/scentify.git
git branch -M main
git push -u origin main
```

### **Step 2: Deploy on Streamlit Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Configure your deployment:
   - **Repository:** Select your `scentify` repository
   - **Branch:** `main`
   - **Main file path:** `app.py`

### **Step 3: Add API Key Secret**

1. In **Advanced settings**, expand **"Secrets"**
2. Add the following in the secrets editor:

```toml
FRAGELLA_API_KEY = "62f95dd0dbd0d644b84131cb5eb9a274eb8decc5202e6a329bea1923eef14430"
```

3. Click **"Save"**
4. Click **"Deploy!"**

Your app will be live at: `https://YOUR_USERNAME-scentify.streamlit.app`

---

## 📊 Fragella API Integration

### **Important: Correct Field Mappings**

The Fragella API uses **PascalCase with spaces** for field names. This app correctly maps all API fields:

#### **Perfume Object Fields:**

```python
{
    "Name": "Dior Sauvage",                    # string
    "Brand": "Christian Dior",                 # string
    "Image URL": "https://...",                # string (.jpg → .webp for transparency)
    "Gender": "men",                           # string (women/men/unisex)
    "Price": "120.00",                         # string
    "Longevity": "Long Lasting",               # string (Poor/Weak/Moderate/Long Lasting/Very Long Lasting)
    "Sillage": "Strong",                       # string (Intimate/Soft/Moderate/Strong/Enormous)
    "OilType": "Eau de Parfum",                # string (may be empty)
    "General Notes": ["bergamot", "pepper"],   # array of strings
    "Main Accords": ["fresh", "spicy", "woody"], # array of strings (ordered by prominence)
    "Main Accords Percentage": {               # object mapping accord → strength
        "fresh": "Dominant",
        "spicy": "Prominent",
        "woody": "Moderate"
    },
    "Notes": {                                 # object with note arrays
        "Top": [{"name": "Bergamot", "imageUrl": "..."}],
        "Middle": [{"name": "Pepper", "imageUrl": "..."}],
        "Base": [{"name": "Ambroxan", "imageUrl": "..."}]
    },
    "Season Ranking": [                        # array of {name, score} objects
        {"name": "spring", "score": 2.384},
        {"name": "summer", "score": 2.019}
    ],
    "Occasion Ranking": [                      # array of {name, score} objects
        {"name": "casual", "score": 2.980},
        {"name": "night out", "score": 1.418}
    ],
    "Image Fallbacks": ["https://..."],        # optional array
    "Purchase URL": "https://..."              # optional string
}
```

#### **Accord Strength Descriptors:**

- **Dominant**: Most powerful and defining accord
- **Prominent**: Very strong, shapes character
- **Moderate**: Clearly detectable
- **Subtle**: Background accord
- **Trace**: Very faint hint

---

## 📁 Project Structure

```
HSG/
├── app.py                          # Landing page (entry point)
├── pages/
│   ├── 01_Search.py               # Search & filter
│   ├── 02_Questionnaire.py        # AI recommendations
│   └── 03_Inventory.py            # Collection management
├── utils/
│   ├── api_client.py              # Fragella API wrapper (CORRECTED)
│   ├── recommender.py             # ML recommendation engine
│   └── ui_helpers.py              # UI components (CORRECTED)
├── sample_data/
│   └── perfumes.csv               # Fallback data
├── .streamlit/
│   └── config.toml                # Theme configuration
├── requirements.txt                # Python dependencies
├── .gitignore                     # Git exclusions
└── README.md                      # This file
```

---

## 🛠️ Technology Stack

- **Framework:** Streamlit 1.40+
- **Data:** Pandas 2.2+, NumPy 1.26+
- **ML:** scikit-learn 1.5+ (cosine similarity)
- **Visualization:** Plotly 5.24+
- **HTTP:** Requests 2.32+
- **API:** Fragella API v1

---

## 🔑 API Endpoints Used

1. **GET /usage** - API quota tracking
2. **GET /fragrances?search=...&limit=...** - Search fragrances
3. **GET /fragrances/match?accords=...&limit=...** - Match by accords
4. **GET /fragrances/similar?name=...&limit=...** - Find similar perfumes
5. **GET /brands/:brandName?limit=...** - Get brand fragrances
6. **GET /notes?search=...&limit=...** - Search notes
7. **GET /accords?search=...&limit=...** - Search accords

---

## 💡 Key Implementation Details

### **Transparent Images**

Per API docs, change `.jpg` to `.webp` in "Image URL" for transparent backgrounds:

```python
def get_transparent_image_url(image_url: str) -> str:
    if image_url.endswith(".jpg"):
        return image_url.replace(".jpg", ".webp")
    return image_url
```

### **Accord Matching**

The questionnaire maps user preferences to accord:percentage pairs for the `/fragrances/match` endpoint:

```python
# Example: "floral:90,fruity:80,citrus:70"
match_fragrances(accords="floral:90,fruity:80,citrus:70", limit=10)
```

### **ML Recommendation**

Uses accord vectors with weights from "Main Accords Percentage":

```python
ACCORD_WEIGHTS = {
    "Dominant": 1.0,
    "Prominent": 0.8,
    "Moderate": 0.6,
    "Subtle": 0.3,
    "Trace": 0.1
}
```

---

## 🐛 Common Issues & Solutions

### **Issue: "API key not found"**
**Solution:** Ensure `FRAGELLA_API_KEY` is set in Streamlit Cloud secrets (Advanced settings).

### **Issue: No data displaying**
**Solution:** 
- Check API key is correct
- Verify API quota hasn't been exceeded (check /usage endpoint)
- Check browser console for errors

### **Issue: Images not loading**
**Solution:** 
- Images come from Fragella CDN
- Try `.webp` extension for transparent backgrounds
- Check "Image Fallbacks" array if primary URL fails

### **Issue: Field mapping errors**
**Solution:** 
- This app uses CORRECT field names with PascalCase and spaces
- Access fields like: `perfume.get("Name")`, `perfume.get("Image URL")`
- NOT: `perfume.get("name")` or `perfume.get("image_url")`

---

## 📝 License

This project is for educational and personal use. Fragella API usage is subject to their terms of service.

---

## 🙏 Acknowledgments

- **Fragella API** for comprehensive fragrance data
- **Streamlit** for the amazing web framework
- **Plotly** for interactive charts

---

**Built with ❤️ and Streamlit**

Enjoy discovering your perfect scent! 🌸

