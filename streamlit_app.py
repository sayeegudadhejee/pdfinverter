import streamlit as st
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz
from PIL import Image, ImageOps
import io
import zipfile
from pathlib import Path
import tempfile
import os

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
</style>
""", unsafe_allow_html=True)

def invert_pdf_colors(pdf_bytes, filename):
    """Invert colors in a PDF file"""
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
        st.error(f"Error processing {filename}: {str(e)}")
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
    
    # File uploader
    st.markdown("### 📁 Upload PDF Files")
    uploaded_files = st.file_uploader(
        "Choose PDF files to invert colors",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files. Dark backgrounds will become white, saving ink when printing."
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            st.write(f"📄 {file.name} ({file.size:,} bytes)")
        
        # Processing options
        col1, col2 = st.columns([1, 1])
        
        with col1:
            quality = st.selectbox(
                "Output Quality",
                ["High (2x resolution)", "Standard (1x resolution)"],
                help="Higher quality takes longer but produces better results"
            )
        
        with col2:
            naming = st.selectbox(
                "File Naming",
                ["Add '_inverted' suffix", "Add '_ink_saver' suffix", "Add '_print_ready' suffix"],
                help="How to name the processed files"
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
            status_text.text("✅ Processing complete!")
            
            if processed_files:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"🎉 Successfully processed {len(processed_files)} PDF files!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download options
                st.markdown("### 📥 Download Results")
                
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
                            label=f"📦 Download All as ZIP ({len(processed_files)} files)",
                            data=zip_data,
                            file_name="inverted_pdfs.zip",
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
                                mime="application/pdf",
                                use_container_width=True
                            )
                
                # Show preview info
                st.markdown("### 🔍 What Changed?")
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.info("""
                **Color Inversion Applied:**
                - Black backgrounds → White backgrounds
                - White text → Black text  
                - Dark colors → Light colors
                - Perfect for ink-saving printing!
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.error("❌ No files were successfully processed. Please check your PDF files and try again.")
    
    else:
        # Show example/demo info
        st.markdown("### 🎯 Perfect for Saving Ink!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Presentations**
            - Dark slide backgrounds
            - High contrast themes
            - Corporate templates
            """)
        
        with col2:
            st.markdown("""
            **💻 Code Documents**
            - Dark IDE themes
            - Syntax highlighting
            - Technical documentation
            """)
        
        with col3:
            st.markdown("""
            **📚 Academic Papers**
            - Dark backgrounds
            - Highlighted sections
            - Research documents
            """)
        
        st.markdown("---")
        st.markdown("**💡 Tip:** Upload your PDFs above to get started!")

if __name__ == "__main__":

    main()
