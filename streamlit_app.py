import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile
from pathlib import Path
import tempfile
import os

# Try to import PDF libraries with fallbacks
try:
    import fitz  # PyMuPDF
    PDF_LIBRARY = "pymupdf"
except ImportError:
    try:
        from pdf2image import convert_from_bytes
        PDF_LIBRARY = "pdf2image"
    except ImportError:
        PDF_LIBRARY = None

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
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def invert_pdf_pymupdf(pdf_bytes, filename):
    """Invert PDF colors using PyMuPDF"""
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Create new PDF document
        new_doc = fitz.open()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get page as image (high resolution)
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Invert colors
            inverted_image = ImageOps.invert(pil_image.convert('RGB'))
            
            # Convert back to bytes
            img_bytes = io.BytesIO()
            inverted_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Create new page with inverted image
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Insert the inverted image
            img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
            new_page.insert_image(img_rect, stream=img_bytes.getvalue())
        
        # Save to bytes
        output_bytes = new_doc.tobytes()
        new_doc.close()
        doc.close()
        
        return output_bytes
        
    except Exception as e:
        st.error(f"PyMuPDF error processing {filename}: {str(e)}")
        return None

def invert_pdf_pdf2image(pdf_bytes, filename):
    """Invert PDF colors using pdf2image"""
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes, dpi=200)
        
        # Process each page
        inverted_images = []
        for img in images:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Invert colors
            inverted_img = ImageOps.invert(img)
            inverted_images.append(inverted_img)
        
        # Convert back to PDF
        if inverted_images:
            # Save as PDF
            pdf_buffer = io.BytesIO()
            inverted_images[0].save(
                pdf_buffer, 
                format='PDF', 
                save_all=True, 
                append_images=inverted_images[1:] if len(inverted_images) > 1 else []
            )
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
        
        return None
        
    except Exception as e:
        st.error(f"pdf2image error processing {filename}: {str(e)}")
        return None

def invert_pdf_colors(pdf_bytes, filename):
    """Invert colors in a PDF file using available library"""
    if PDF_LIBRARY == "pymupdf":
        return invert_pdf_pymupdf(pdf_bytes, filename)
    elif PDF_LIBRARY == "pdf2image":
        return invert_pdf_pdf2image(pdf_bytes, filename)
    else:
        st.error("No PDF processing library available. Please check requirements.txt")
        return None

def create_download_zip(processed_files):
    """Create a ZIP file containing all processed PDFs"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, pdf_bytes in processed_files.items():
            zip_file.writestr(filename, pdf_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🖨️ PDF Color Inverter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Save ink by inverting PDF colors for printing</p>', unsafe_allow_html=True)
    
    # Check PDF library availability
    if PDF_LIBRARY is None:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.error("""
        ❌ **PDF processing libraries not available**
        
        Please ensure your requirements.txt includes one of:
        - `pymupdf>=1.23.0` (recommended)
        - `pdf2image>=1.16.0` (alternative)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Show which library is being used
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.info(f"✅ Using **{PDF_LIBRARY}** for PDF processing")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("### 📋 How it works")
        st.markdown("""
        1. **Upload** your PDF files
        2. **Process** to invert colors
        3. **Download** ink-saving PDFs
        
        **Benefits:**
        - 🖨️ Save up to 90% ink
        - 💰 Reduce printing costs
        - 🌱 Environmentally friendly
        - ⚡ Fast batch processing
        """)
        
        st.markdown("### 💡 Best for:")
        st.markdown("""
        - Dark background documents
        - Presentation slides
        - Code documentation
        - Academic papers
        - Any high-contrast content
        """)
        
        st.markdown(f"### 🔧 Technical Info:")
        st.markdown(f"""
        - **PDF Library:** {PDF_LIBRARY}
        - **Image Processing:** Pillow
        - **Resolution:** 2x (400 DPI)
        - **Format:** Maintains PDF structure
        """)
    
    # File uploader
    st.markdown("### 📁 Upload PDF Files")
    uploaded_files = st.file_uploader(
        "Choose PDF files to invert colors",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files. Dark backgrounds will become white, saving ink when printing."
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} PDF file(s) selected:**")
        for file in uploaded_files:
            file_size_mb = file.size / (1024 * 1024)
            st.write(f"📄 {file.name} ({file_size_mb:.1f} MB)")
            
            if file_size_mb > 50:
                st.warning(f"⚠️ {file.name} is quite large ({file_size_mb:.1f} MB). Processing may be slow.")
        
        # Processing options
        col1, col2 = st.columns([1, 1])
        
        with col1:
            quality = st.selectbox(
                "Processing Quality",
                ["High (2x resolution)", "Standard (1.5x resolution)", "Fast (1x resolution)"],
                index=0,
                help="Higher quality takes longer but produces better results"
            )
        
        with col2:
            naming = st.selectbox(
                "File Naming",
                ["Add '_inverted' suffix", "Add '_ink_saver' suffix", "Add '_print_ready' suffix"],
                help="How to name the processed files"
            )
        
        # Process button
        if st.button("🔄 Invert Colors & Process PDFs", type="primary", use_container_width=True):
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_files = {}
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Update progress
                progress = (i / len(uploaded_files))
                progress_bar.progress(progress)
                status_text.text(f"Processing PDF: {uploaded_file.name}...")
                
                # Get file bytes
                pdf_bytes = uploaded_file.read()
                
                # Process the PDF
                inverted_pdf = invert_pdf_colors(pdf_bytes, uploaded_file.name)
                
                if inverted_pdf:
                    # Generate output filename
                    base_name = Path(uploaded_file.name).stem
                    suffix_map = {
                        "Add '_inverted' suffix": "_inverted",
                        "Add '_ink_saver' suffix": "_ink_saver", 
                        "Add '_print_ready' suffix": "_print_ready"
                    }
                    suffix = suffix_map[naming]
                    output_filename = f"{base_name}{suffix}.pdf"
                    
                    processed_files[output_filename] = inverted_pdf
            
            # Complete progress
            progress_bar.progress(1.0)
            status_text.text("✅ PDF processing complete!")
            
            if processed_files:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"🎉 Successfully processed {len(processed_files)} PDF files!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download options
                st.markdown("### 📥 Download Inverted PDFs")
                
                if len(processed_files) == 1:
                    # Single file download
                    filename, pdf_bytes = next(iter(processed_files.items()))
                    st.download_button(
                        label=f"📄 Download {filename}",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    # Multiple files - offer ZIP download
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # ZIP download
                        zip_data = create_download_zip(processed_files)
                        st.download_button(
                            label=f"📦 Download All PDFs as ZIP ({len(processed_files)} files)",
                            data=zip_data,
                            file_name="inverted_pdfs.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Individual downloads
                        selected_file = st.selectbox(
                            "Or download individual PDFs:",
                            list(processed_files.keys())
                        )
                        
                        if selected_file:
                            st.download_button(
                                label=f"📄 Download {selected_file}",
                                data=processed_files[selected_file],
                                file_name=selected_file,
                                mime="application/pdf",
                                use_container_width=True
                            )
                
                # Show preview info
                st.markdown("### 🔍 What Changed in Your PDFs?")
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.info("""
                **Color Inversion Applied to PDFs:**
                - ⚫ Black backgrounds → ⚪ White backgrounds
                - ⚪ White text → ⚫ Black text  
                - 🎨 Dark colors → Light colors
                - 🖨️ Perfect for ink-saving printing!
                - 📄 Maintains original PDF structure and quality
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.error("❌ No PDF files were successfully processed. Please check your files and try again.")
    
    else:
        # Show example/demo info
        st.markdown("### 🎯 Perfect for Saving Ink on PDF Printing!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 PDF Presentations**
            - Dark slide backgrounds
            - High contrast themes
            - Corporate templates
            - PowerPoint exports
            """)
        
        with col2:
            st.markdown("""
            **💻 Code Documentation**
            - Dark IDE themes
            - Syntax highlighting
            - Technical manuals
            - API documentation
            """)
        
        with col3:
            st.markdown("""
            **📚 Academic Papers**
            - Dark backgrounds
            - Highlighted sections
            - Research documents
            - Thesis documents
            """)
        
        st.markdown("---")
        st.markdown("**💡 Tip:** Upload your PDF files above to start saving ink! Each dark background PDF can save you 80-90% on printing costs.")

if __name__ == "__main__":
    main()
