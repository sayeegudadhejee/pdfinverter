# 🖨️ PDF Color Inverter - Streamlit Web App

A web-based PDF color inverter that saves ink by converting dark backgrounds to white. Perfect for printing presentations, code docs, and academic papers without wasting expensive ink!

## 🚀 Quick Deploy to Streamlit Cloud

### Option 1: Deploy Your Own (Recommended)

1. **Fork/Upload to GitHub:**
   - Create a new GitHub repository
   - Upload these files: `streamlit_app.py` and `requirements_streamlit.txt`

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repo
   - Set main file: `streamlit_app.py`
   - Click "Deploy"

3. **Done!** Your app will be live at `https://[your-app-name].streamlit.app`

### Option 2: Run Locally

```bash
pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

## ✨ Features

- **🔄 Batch Processing** - Handle multiple PDFs at once
- **💾 Multiple Downloads** - Individual files or ZIP bundle
- **⚡ Fast Processing** - High-quality color inversion
- **📱 Mobile Friendly** - Works on any device
- **🔒 Privacy First** - Files processed in browser, not stored
- **🎨 Beautiful UI** - Clean, professional interface

## 🎯 Perfect For

- **Presentations** with dark backgrounds
- **Code documentation** with syntax highlighting  
- **Academic papers** with dark themes
- **Any PDF** that wastes ink when printing

## 💡 How It Works

1. **Upload** your PDF files (drag & drop supported)
2. **Choose** quality and naming options
3. **Process** - colors get inverted automatically
4. **Download** your ink-saving PDFs

**Result:** Dark backgrounds become white, saving up to 90% of your printing ink!

## 🛠️ Technical Details

- Built with **Streamlit** for easy deployment
- Uses **PyMuPDF** for PDF processing
- **PIL/Pillow** for image color inversion
- Processes at 2x resolution for quality
- No server storage - everything in memory

## 📋 File Structure

```
├── streamlit_app.py           # Main web application
├── requirements_streamlit.txt # Dependencies for deployment
└── README_STREAMLIT.md       # This file
```

## 🌐 Deployment Platforms

This app works on:
- **Streamlit Cloud** (Free, recommended)
- **Heroku** 
- **Railway**
- **Render**
- **Any Python hosting service**

## 🔧 Customization

Want to modify the app? Key areas to customize:

- **UI Colors:** Modify the CSS in the `st.markdown()` sections
- **Processing Quality:** Change the `Matrix(2.0, 2.0)` values
- **File Naming:** Update the suffix options
- **Upload Limits:** Streamlit Cloud has 200MB file limits

## 🚨 Important Notes

- **File Size Limits:** Streamlit Cloud limits uploads to 200MB per file
- **Processing Time:** Large PDFs may take 30-60 seconds
- **Memory Usage:** Very large files might hit memory limits
- **Privacy:** Files are processed in memory and not stored anywhere

## 🎉 Ready to Deploy?

1. Copy `streamlit_app.py` and `requirements_streamlit.txt` to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your repo
4. Share your app URL with anyone who needs to save ink!

Your users can now invert PDF colors from any device, anywhere in the world! 🌍