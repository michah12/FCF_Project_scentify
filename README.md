# 🌸 SCENTIFY - Perfume Finder & Recommendation App

A beautiful, intelligent Streamlit web application for discovering and managing your perfect fragrances, powered by the Fragella API.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## ✨ Features

### 🔍 **Search**
- Search perfumes by name, brand, or keyword
- Advanced filters: brand, gender, price range, scent types
- Detailed perfume information with notes breakdown
- ML-powered personalized ranking based on your preferences

### 📋 **Questionnaire**
- Answer 5 simple questions about your preferences
- AI-powered recommendations based on your answers
- Preference mapping to fragrance accords

### 📚 **Perfume Inventory**
- Build your personal fragrance collection
- Visual analytics with interactive charts:
  - Note composition (Top, Heart, Base)
  - Seasonal preferences
  - Occasion breakdown
- Collection statistics and insights

### 🤖 **Machine Learning**
- Content-based recommender using accord vectors
- Learns from your clicks and preferences
- Cosine similarity ranking for personalized results

---

## 🚀 Deployment to Streamlit Cloud

Follow these steps to deploy SCENTIFY on Streamlit Cloud from GitHub:

### **Step 1: Push to GitHub**

1. Create a new GitHub repository (e.g., `scentify-app`)
2. Initialize Git in your project directory:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: SCENTIFY perfume app"
   ```
3. Connect to your GitHub repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/scentify-app.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Deploy on Streamlit Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Configure your deployment:
   - **Repository:** Select your `scentify-app` repository
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Advanced settings"** (optional: set Python version to 3.10+)

### **Step 3: Add API Key Secret**

1. In the **Advanced settings** section, expand **"Secrets"**
2. Add the following in the secrets editor:
   ```toml
   FRAGELLA_API_KEY = "62f95dd0dbd0d644b84131cb5eb9a274eb8decc5202e6a329bea1923eef14430"
   ```
3. Click **"Save"**

### **Step 4: Deploy!**

1. Click **"Deploy!"**
2. Wait for the app to build and deploy (usually 2-3 minutes)
3. Your app will be live at: `https://YOUR_USERNAME-scentify-app.streamlit.app`

---

## 📁 Project Structure

```
SCENTIFY/
│
├── app.py                      # Main landing page (entry point)
│
├── pages/                      # Multi-page app structure
│   ├── 01_Search.py           # Search and filter perfumes
│   ├── 02_Questionnaire.py    # Preference-based recommendations
│   └── 03_Inventory.py        # Personal collection with analytics
│
├── utils/                      # Utility modules
│   ├── api_client.py          # Fragella API wrapper
│   ├── recommender.py         # ML-based recommendation engine
│   └── ui_helpers.py          # Reusable UI components
│
├── sample_data/                # Fallback data
│   └── perfumes.csv           # Sample perfume data
│
├── .streamlit/                 # Streamlit configuration
│   └── config.toml            # Theme and settings
│
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

---

## 🛠️ Local Development (Optional)

If you want to run the app locally before deploying:

### **Prerequisites**
- Python 3.10 or higher
- pip (Python package manager)

### **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/scentify-app.git
   cd scentify-app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml`:
   ```bash
   mkdir -p .streamlit
   echo 'FRAGELLA_API_KEY = "62f95dd0dbd0d644b84131cb5eb9a274eb8decc5202e6a329bea1923eef14430"' > .streamlit/secrets.toml
   ```

5. Run the app:
   ```bash
   streamlit run app.py
   ```

6. Open your browser to `http://localhost:8501`

---

## 🎨 Technology Stack

- **Framework:** Streamlit 1.40+
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly
- **Machine Learning:** scikit-learn (cosine similarity)
- **API Integration:** Fragella API v1
- **HTTP Client:** Requests

---

## 🔑 API Information

**Fragella API Documentation:** https://api.fragella.com/docs

### Available Endpoints Used:
- `GET /usage` - API quota information
- `GET /fragrances?search=...` - Search fragrances
- `GET /fragrances/match?accords=...` - Match by accords
- `GET /fragrances/similar?name=...` - Find similar perfumes
- `GET /brands/:brandName` - Get brand fragrances
- `GET /notes?search=...` - Search notes
- `GET /accords?search=...` - Search accords

---

## 📊 Features in Detail

### **Search Page**
- Real-time search with 3+ character minimum
- Multi-filter support (brand, gender, price, accords)
- Click tracking for ML recommendations
- Beautiful card layout with images

### **Questionnaire**
- 5-slider interface for preference capture:
  1. Intensity (Subtle ↔ Bold)
  2. Temperature (Fresh ↔ Warm)
  3. Sweetness (Dry ↔ Sweet)
  4. Occasion (Daily ↔ Evening)
  5. Style (Feminine ↔ Masculine)
- Intelligent accord mapping
- Personalized result ranking

### **Inventory**
- Add/remove perfumes to your collection
- Visual analytics:
  - **Donut charts** for note composition
  - **Bar charts** for seasons and occasions
- Collection statistics
- Session-persistent storage

### **ML Recommender**
- Accord-based vector representation
- User profile built from click history
- Cosine similarity ranking
- Real-time learning from interactions

---

## 🎯 Usage Tips

1. **Start with Search** - Explore perfumes by name or brand
2. **Use Questionnaire** - Get personalized recommendations without prior knowledge
3. **Build Inventory** - Add favorites to see your scent profile
4. **Click to Learn** - The more you interact, the better recommendations you'll get

---

## 🔒 Security & Privacy

- API keys stored securely in Streamlit secrets
- No external databases - all data in session state
- No user data collection or tracking
- HTTPS encryption on Streamlit Cloud

---

## 📝 License

This project is for educational and personal use. Fragella API usage is subject to their terms of service.

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Fork and submit pull requests
- Share your experience using SCENTIFY

---

## 📧 Contact

For questions or feedback about this project, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- **Fragella API** for providing comprehensive fragrance data
- **Streamlit** for the amazing web framework
- **Plotly** for beautiful interactive charts

---

**Built with ❤️ and Streamlit**

Enjoy discovering your perfect scent! 🌸

