# 🚀 Deploy PDF Color Inverter to Streamlit Cloud

## Step-by-Step Deployment Guide

### 1. Prepare Your Files
You need these 2 files:
- `streamlit_app.py` (the main app)
- `requirements_streamlit.txt` (dependencies)

### 2. Upload to GitHub
1. Go to [github.com](https://github.com) and create a new repository
2. Name it something like `pdf-color-inverter`
3. Upload both files above

### 3. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account
4. Select your repository
5. Set **Main file path:** `streamlit_app.py`
6. Click **"Deploy!"**

### 4. Your App is Live! 🎉
- URL will be: `https://[your-repo-name].streamlit.app`
- Share this URL with anyone
- Works on mobile, tablet, desktop

## 🔧 Alternative: Run Locally First

Test it on your computer:
```bash
pip install streamlit PyMuPDF Pillow
streamlit run streamlit_app.py
```

## 💡 Pro Tips

- **Custom URL:** Rename your GitHub repo to get a better URL
- **Updates:** Push changes to GitHub and Streamlit auto-updates
- **Analytics:** Streamlit Cloud shows usage stats
- **Free Tier:** Unlimited public apps, 1GB storage

## 🌐 Your App Features

Once deployed, users can:
- Upload multiple PDFs (drag & drop)
- Choose quality settings
- Download individual files or ZIP bundle
- Use on any device with internet
- Process files privately (nothing stored on server)

## 🎯 Perfect for Sharing

Send your app URL to:
- Colleagues who print a lot
- Students with expensive printer ink
- Anyone who wants to save money on printing
- Teachers preparing handouts

**No installation needed for users - just visit the URL and start saving ink!** 🖨️💰