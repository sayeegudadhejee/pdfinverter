import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile
from pathlib import Path
import base64

# Page config
st.set_page_config(
    page_title="PDF Color Inverter",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def process_image_file(image_bytes, filename):
    """Process image files and invert colors"""
    try:
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Invert colors
        inverted_image = ImageOps.invert(image)
        
        # Save to bytes
        output_buffer = io.BytesIO()
        
        # Save as PNG for best quality
        inverted_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error processing {filename}: {str(e)}")
        return None

def create_download_zip(processed_files):
    """Create a ZIP file containing all processed files"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, file_bytes in processed_files.items():
            zip_file.writestr(filename, file_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    # Header
    st.markdown('<h1 class="main-header">🖨️ PDF Color Inverter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Save ink by inverting colors for printing</p>', unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("### 📋 How it works")
        st.markdown("""
        1. **Convert** PDF to images first
        2. **Upload** the images here
        3. **Process** to invert colors
        4. **Download** ink-saving images
        
        **Benefits:**
        - 🖨️ Save up to 90% ink
        - 💰 Reduce printing costs
        - 🌱 Environmentally friendly
        - ⚡ Fast processing
        """)
        
        st.markdown("### 🔧 PDF to Image Tools:")
        st.markdown("""
        **Online converters:**
        - [SmallPDF](https://smallpdf.com/pdf-to-jpg)
        - [ILovePDF](https://www.ilovepdf.com/pdf_to_jpg)
        - [PDF24](https://tools.pdf24.org/en/pdf-to-images)
        
        **Or use screenshots!**
        """)
    
    # Instructions for PDF users
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.info("""
    **📄 For PDF files:** First convert your PDF to images using any online PDF-to-image converter, then upload the images here.
    
    **🖼️ For images:** Upload PNG, JPG, or screenshots directly!
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File uploader
    st.markdown("### 📁 Upload Image Files")
    uploaded_files = st.file_uploader(
        "Choose image files to invert colors",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        accept_multiple_files=True,
        help="Upload images from PDF pages, screenshots, or any image files with dark backgrounds."
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        
        # Show preview of uploaded files
        if len(uploaded_files) <= 6:
            cols = st.columns(min(len(uploaded_files), 3))
            for i, file in enumerate(uploaded_files):
                with cols[i % 3]:
                    try:
                        image = Image.open(file)
                        st.image(image, caption=file.name, use_column_width=True)
                        file_size_mb = file.size / (1024 * 1024)
                        st.caption(f"{file_size_mb:.1f} MB")
                    except:
                        st.write(f"📄 {file.name}")
        else:
            for file in uploaded_files:
                file_size_mb = file.size / (1024 * 1024)
                st.write(f"📄 {file.name} ({file_size_mb:.1f} MB)")
        
        # Reset file pointers
        for file in uploaded_files:
            file.seek(0)
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            naming = st.selectbox(
                "Output File Naming",
                ["Add '_inverted' suffix", "Add '_ink_saver' suffix", "Add '_print_ready' suffix"],
                help="How to name the processed files"
            )
        
        with col2:
            output_format = st.selectbox(
                "Output Format",
                ["PNG (Best Quality)", "JPG (Smaller Size)"],
                help="Choose output file format"
            )
        
        # Process button
        if st.button("🔄 Invert Colors & Process", type="primary", use_container_width=True):
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_files = {}
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Update progress
                progress = (i / len(uploaded_files))
                progress_bar.progress(progress)
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Get file bytes
                file_bytes = uploaded_file.read()
                
                # Process the image
                inverted_image = process_image_file(file_bytes, uploaded_file.name)
                
                if inverted_image:
                    # Generate output filename
                    base_name = Path(uploaded_file.name).stem
                    
                    # Determine suffix
                    suffix_map = {
                        "Add '_inverted' suffix": "_inverted",
                        "Add '_ink_saver' suffix": "_ink_saver", 
                        "Add '_print_ready' suffix": "_print_ready"
                    }
                    suffix = suffix_map[naming]
                    
                    # Determine extension
                    if output_format == "PNG (Best Quality)":
                        ext = ".png"
                    else:
                        ext = ".jpg"
                    
                    output_filename = f"{base_name}{suffix}{ext}"
                    processed_files[output_filename] = inverted_image
            
            # Complete progress
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")
            
            if processed_files:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"🎉 Successfully processed {len(processed_files)} files!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Show before/after preview
                st.markdown("### 🔍 Before & After Preview")
                if len(uploaded_files) > 0:
                    preview_file = uploaded_files[0]
                    preview_file.seek(0)
                    original_image = Image.open(preview_file)
                    inverted_preview = ImageOps.invert(original_image.convert('RGB'))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Before (Original)**")
                        st.image(original_image, use_column_width=True)
                    with col2:
                        st.markdown("**After (Inverted - Ink Saving!)**")
                        st.image(inverted_preview, use_column_width=True)
                
                # Download options
                st.markdown("### 📥 Download Results")
                
                if len(processed_files) == 1:
                    # Single file download
                    filename, file_bytes = next(iter(processed_files.items()))
                    st.download_button(
                        label=f"📄 Download {filename}",
                        data=file_bytes,
                        file_name=filename,
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    # Multiple files - offer ZIP download
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # ZIP download
                        zip_data = create_download_zip(processed_files)
                        st.download_button(
                            label=f"📦 Download All as ZIP ({len(processed_files)} files)",
                            data=zip_data,
                            file_name="inverted_images.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Individual downloads
                        selected_file = st.selectbox(
                            "Or download individual files:",
                            list(processed_files.keys())
                        )
                        
                        if selected_file:
                            st.download_button(
                                label=f"📄 Download {selected_file}",
                                data=processed_files[selected_file],
                                file_name=selected_file,
                                mime="image/png",
                                use_container_width=True
                            )
                
                # Show what changed
                st.markdown("### ✨ What Changed?")
                st.info("""
                **Color Inversion Applied:**
                - ⚫ Black backgrounds → ⚪ White backgrounds  
                - ⚪ White text → ⚫ Black text
                - 🎨 Dark colors → Light colors
                - 🖨️ Perfect for ink-saving printing! Save 80-90% on ink costs!
                """)
            
            else:
                st.error("❌ No files were successfully processed. Please check your image files and try again.")
    
    else:
        # Show upload instructions
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        st.markdown("""
        ### 📤 Ready to Save Ink?
        
        **For PDF files:**
        1. Convert PDF to images using [SmallPDF](https://smallpdf.com/pdf-to-jpg) or similar
        2. Upload the images here
        3. Download inverted versions
        
        **For images/screenshots:**
        - Just drag and drop above!
        
        **Perfect for:**
        - 📊 Dark presentation slides
        - 💻 Code screenshots  
        - 📚 Academic papers
        - 🎨 Any dark background content
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Example benefits
        st.markdown("### 💡 Why Invert Colors?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **💰 Save Money**
            - Up to 90% less ink usage
            - Reduce printing costs
            - Extend cartridge life
            """)
        
        with col2:
            st.markdown("""
            **🌱 Eco-Friendly**
            - Less ink waste
            - Fewer cartridge replacements
            - Reduce environmental impact
            """)
        
        with col3:
            st.markdown("""
            **📖 Better Reading**
            - Dark text on white background
            - Easier on the eyes
            - Professional appearance
            """)

if __name__ == "__main__":
    main()
