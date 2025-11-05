# 🚀 SCENTIFY - Deployment Checklist

Follow this checklist to deploy your SCENTIFY app to Streamlit Cloud.

---

## ✅ Pre-Deployment Checklist

- [ ] All files are present in the project directory:
  - [ ] `app.py`
  - [ ] `pages/01_Search.py`
  - [ ] `pages/02_Questionnaire.py`
  - [ ] `pages/03_Inventory.py`
  - [ ] `utils/api_client.py`
  - [ ] `utils/recommender.py`
  - [ ] `utils/ui_helpers.py`
  - [ ] `sample_data/perfumes.csv`
  - [ ] `.streamlit/config.toml`
  - [ ] `requirements.txt`
  - [ ] `README.md`
  - [ ] `.gitignore`

- [ ] Python syntax verified (no errors)
- [ ] API key ready: `62f95dd0dbd0d644b84131cb5eb9a274eb8decc5202e6a329bea1923eef14430`

---

## 📦 Step 1: Push to GitHub

### Option A: New Repository

```bash
# Navigate to project directory
cd /Users/michahansli/Desktop/HSG

# Initialize Git (if not already initialized)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: SCENTIFY perfume finder app"

# Create repository on GitHub.com (via web interface)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/scentify.git
git branch -M main
git push -u origin main
```

### Option B: Existing Repository

```bash
# Navigate to project directory
cd /Users/michahansli/Desktop/HSG

# Add and commit changes
git add .
git commit -m "Add SCENTIFY perfume finder app"
git push
```

**✅ Check:** Verify all files are visible on GitHub

---

## ☁️ Step 2: Deploy on Streamlit Cloud

### 2.1 Access Streamlit Cloud
1. Go to: [https://share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit Cloud to access your repositories

### 2.2 Create New App
1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository:** Select `YOUR_USERNAME/scentify` (or your repo name)
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Choose a custom URL or use auto-generated

### 2.3 Configure Advanced Settings
1. Click **"Advanced settings"**
2. **Python version:** Select `3.10` or higher (recommended: `3.11`)
3. **Secrets:** Click to expand the secrets section
4. Add the following in the secrets editor:

```toml
FRAGELLA_API_KEY = "62f95dd0dbd0d644b84131cb5eb9a274eb8decc5202e6a329bea1923eef14430"
```

5. Click **"Save"**

### 2.4 Deploy
1. Click the **"Deploy!"** button
2. Wait for deployment (typically 2-5 minutes)
3. Watch the build logs for any errors

**✅ Check:** App should start building automatically

---

## 🎉 Step 3: Verify Deployment

### 3.1 Check Build Status
- [ ] Build completed successfully (green checkmark)
- [ ] No error messages in build logs
- [ ] App is running

### 3.2 Test Core Features
- [ ] Landing page loads with three navigation cards
- [ ] Search page works (try searching "Chanel")
- [ ] Questionnaire page displays 5 sliders
- [ ] Inventory page shows empty state
- [ ] API usage footer displays (if API is working)

### 3.3 Test Search Functionality
- [ ] Search for "Dior" returns results
- [ ] Can click on perfume to view details
- [ ] Can add perfume to inventory
- [ ] Filters work (gender, price, accords)

### 3.4 Test Questionnaire
- [ ] All 5 sliders respond to input
- [ ] "Get Recommendations" button works
- [ ] Results are displayed
- [ ] Can view perfume details from results

### 3.5 Test Inventory
- [ ] Can add perfumes to collection
- [ ] Charts display when collection has items
- [ ] Can view perfume details
- [ ] Can remove perfumes from collection

---

## 🔧 Troubleshooting

### Issue: "API key not found"
**Solution:** 
- Check that you added the secret in Streamlit Cloud settings
- Ensure the key name is exactly: `FRAGELLA_API_KEY`
- No quotes around the key name in secrets.toml
- Restart the app after adding secrets

### Issue: "Module not found"
**Solution:**
- Verify `requirements.txt` is present in repository
- Check that all dependencies are listed
- Try redeploying the app (click "Reboot" in app menu)

### Issue: "Import error" or "No module named 'utils'"
**Solution:**
- Ensure `utils/` directory structure is correct
- Check that `utils/` folder is pushed to GitHub
- Verify file names match exactly (case-sensitive)

### Issue: API requests failing
**Solution:**
- Check API key is correct in secrets
- Verify Fragella API is accessible
- Check API quota hasn't been exceeded
- Sample CSV data should load as fallback

### Issue: Pages not showing in navigation
**Solution:**
- Ensure `pages/` folder exists in repository
- Verify page files start with numbers: `01_`, `02_`, `03_`
- Check that files are in the `pages/` directory, not subdirectories

---

## 📊 Post-Deployment

### Monitor Your App
- **App URL:** `https://YOUR_USERNAME-scentify.streamlit.app`
- **Streamlit Dashboard:** Monitor usage and performance
- **Logs:** Check for errors in real-time

### Share Your App
- [ ] Copy the deployment URL
- [ ] Test on different devices (mobile, tablet, desktop)
- [ ] Share with friends or users
- [ ] Gather feedback

### Optional Enhancements
- [ ] Add custom domain (Streamlit Pro)
- [ ] Enable authentication (Streamlit Pro)
- [ ] Add analytics tracking
- [ ] Expand perfume database
- [ ] Add user reviews feature

---

## 🎓 Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Fragella API Docs:** https://api.fragella.com/docs
- **Project README:** See `README.md` in repository

---

## ✨ Success Criteria

Your deployment is successful when:
- ✅ App is accessible via public URL
- ✅ All three pages load without errors
- ✅ API integration works (or fallback data loads)
- ✅ User can search, get recommendations, and manage inventory
- ✅ Charts and visualizations display correctly
- ✅ Mobile responsive (test on phone)

---

**🌸 Congratulations! Your SCENTIFY app is now live! 🌸**

Enjoy helping users find their perfect fragrance!

