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
    layout="wide"
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
    .upload-box {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
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
        
        # Determine format from filename
        file_ext = Path(filename).suffix.lower()
        if file_ext in ['.jpg', '.jpeg']:
            format_type = 'JPEG'
        elif file_ext == '.png':
            format_type = 'PNG'
        elif file_ext == '.pdf':
            format_type = 'PDF'
        else:
            format_type = 'PNG'  # Default
        
        inverted_image.save(output_buffer, format=format_type)
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
    st.markdown('<h1 class="main-header">🖨️ Image Color Inverter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Save ink by inverting image colors for printing</p>', unsafe_allow_html=True)
    
    # Info section
    st.markdown("### 🎯 How It Works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📤 Upload**
        - Images (PNG, JPG)
        - Screenshots
        - Scanned documents
        """)
    
    with col2:
        st.markdown("""
        **🔄 Process**
        - Invert all colors
        - Dark → Light
        - Light → Dark
        """)
    
    with col3:
        st.markdown("""
        **💾 Download**
        - Individual files
        - ZIP bundle
        - Ready to print!
        """)
    
    st.markdown("---")
    
    # File uploader
    st.markdown("### 📁 Upload Image Files")
    uploaded_files = st.file_uploader(
        "Choose image files to invert colors",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Upload PNG, JPG, or JPEG files. Dark backgrounds will become white to save ink."
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        
        # Show preview of uploaded files
        cols = st.columns(min(len(uploaded_files), 4))
        for i, file in enumerate(uploaded_files):
            with cols[i % 4]:
                try:
                    image = Image.open(file)
                    st.image(image, caption=file.name, use_column_width=True)
                    file_size_mb = file.size / (1024 * 1024)
                    st.caption(f"{file_size_mb:.1f} MB")
                except:
                    st.write(f"📄 {file.name}")
        
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
                ["Keep original format", "Convert all to PNG", "Convert all to JPG"],
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
                    original_ext = Path(uploaded_file.name).suffix
                    
                    # Determine suffix
                    suffix_map = {
                        "Add '_inverted' suffix": "_inverted",
                        "Add '_ink_saver' suffix": "_ink_saver", 
                        "Add '_print_ready' suffix": "_print_ready"
                    }
                    suffix = suffix_map[naming]
                    
                    # Determine extension
                    if output_format == "Convert all to PNG":
                        ext = ".png"
                    elif output_format == "Convert all to JPG":
                        ext = ".jpg"
                    else:
                        ext = original_ext
                    
                    output_filename = f"{base_name}{suffix}{ext}"
                    processed_files[output_filename] = inverted_image
            
            # Complete progress
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")
            
            if processed_files:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"🎉 Successfully processed {len(processed_files)} image files!")
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
                        st.markdown("**After (Inverted)**")
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
                - Black backgrounds → White backgrounds  
                - White text → Black text
                - Dark colors → Light colors
                - Perfect for ink-saving printing! 🖨️💰
                """)
            
            else:
                st.error("❌ No files were successfully processed. Please check your image files and try again.")
    
    else:
        # Show upload area
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 📤 Ready to Save Ink?
        
        **Perfect for:**
        - Screenshots with dark themes
        - Presentation slides with dark backgrounds  
        - Code snippets with syntax highlighting
        - Any image that would waste ink when printing
        
        **Drag and drop your images above or click to browse!**
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
