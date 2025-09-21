import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile
from pathlib import Path
import base64
import tempfile
import os

# Try to import PDF processing libraries with multiple fallbacks
PDF_SUPPORT = False
PDF_LIBRARY = None

# Method 1: Try pdf2image (works better on cloud platforms)
try:
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
    PDF_LIBRARY = "pdf2image"
except ImportError:
    # Method 2: Try PyMuPDF
    try:
        import fitz
        PDF_SUPPORT = True
        PDF_LIBRARY = "pymupdf"
    except ImportError:
        try:
            import pymupdf as fitz
            PDF_SUPPORT = True
            PDF_LIBRARY = "pymupdf"
        except ImportError:
            pass

if not PDF_SUPPORT:
    st.warning("⚠️ PDF processing not available. Only image files are supported.")
    st.info("""
    **To enable PDF support, you can:**
    1. Convert your PDF to images using online tools like [SmallPDF](https://smallpdf.com/pdf-to-jpg)
    2. Upload the images directly to this app
    3. Or take screenshots of your PDF pages
    """)

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
    .pdf-page-preview {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.5rem 0;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def convert_pdf_to_images(pdf_bytes, dpi=200):
    """Convert PDF to images using available PDF library"""
    if not PDF_SUPPORT:
        st.error("PDF processing not available. Please upload images instead.")
        return []
    
    try:
        if PDF_LIBRARY == "pdf2image":
            # Use pdf2image (more reliable on cloud platforms)
            images_pil = convert_from_bytes(
                pdf_bytes, 
                dpi=dpi,
                fmt='PNG',
                thread_count=1  # Avoid threading issues on cloud
            )
            
            images = []
            for i, img in enumerate(images_pil):
                images.append((img, f"page_{i + 1}"))
            
            return images
            
        elif PDF_LIBRARY == "pymupdf":
            # Use PyMuPDF as fallback
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append((img, f"page_{page_num + 1}"))
            
            pdf_document.close()
            return images
    
    except Exception as e:
        st.error(f"Error converting PDF with {PDF_LIBRARY}: {str(e)}")
        return []

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

def process_pil_image(image, filename):
    """Process PIL Image objects and invert colors"""
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Invert colors
        inverted_image = ImageOps.invert(image)
        
        # Save to bytes
        output_buffer = io.BytesIO()
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
    st.markdown('<p class="sub-header">Save ink by inverting colors for printing - Now with automatic PDF processing!</p>', unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("### 📋 How it works")
        if PDF_SUPPORT:
            st.markdown(f"""
            1. **Upload** PDF or image files directly
            2. **Convert** PDF pages to images automatically (using {PDF_LIBRARY})
            3. **Process** to invert colors
            4. **Download** ink-saving images
            
            **Benefits:**
            - 🖨️ Save up to 90% ink
            - 💰 Reduce printing costs
            - 🌱 Environmentally friendly
            - ⚡ Fast processing
            - 📄 Direct PDF support!
            """)
        else:
            st.markdown("""
            1. **Convert** PDF to images first (using online tools)
            2. **Upload** the images here
            3. **Process** to invert colors
            4. **Download** ink-saving images
            
            **Benefits:**
            - 🖨️ Save up to 90% ink
            - 💰 Reduce printing costs
            - 🌱 Environmentally friendly
            - ⚡ Fast processing
            """)
        
        if PDF_SUPPORT:
            st.markdown("### ⚙️ PDF Settings")
            dpi_setting = st.selectbox(
                "Image Quality (DPI)",
                [150, 200, 300],
                index=1,
                help="Higher DPI = better quality but larger files"
            )
        else:
            dpi_setting = 200  # Default value when PDF support is not available
            st.markdown("### 🔧 PDF to Image Tools")
            st.markdown("""
            **Online converters:**
            - [SmallPDF](https://smallpdf.com/pdf-to-jpg)
            - [ILovePDF](https://www.ilovepdf.com/pdf_to_jpg)
            - [PDF24](https://tools.pdf24.org/en/pdf-to-images)
            
            **Or use screenshots!**
            """)
        
        st.markdown("### 💡 Pro Tips")
        if PDF_SUPPORT:
            st.markdown("""
            - **PDF files**: Upload directly - no conversion needed!
            - **Large PDFs**: May take a moment to process
            - **Images**: PNG, JPG, screenshots all supported
            - **Best results**: Dark backgrounds with light text
            """)
        else:
            st.markdown("""
            - **Convert PDFs**: Use online tools first
            - **Screenshots**: Work perfectly!
            - **Images**: PNG, JPG all supported
            - **Best results**: Dark backgrounds with light text
            """)
    
    # Main instructions
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    if PDF_SUPPORT:
        st.info(f"""
        **✅ PDF Support Active** (using {PDF_LIBRARY}): Upload PDF files directly! The app will automatically convert them to images and invert colors.
        
        **Supported formats:** PDF, PNG, JPG, JPEG, BMP, TIFF
        """)
    else:
        st.info("""
        **📄 For PDF files:** First convert your PDF to images using any online PDF-to-image converter, then upload the images here.
        
        **🖼️ For images:** Upload PNG, JPG, or screenshots directly!
        
        **Supported formats:** PNG, JPG, JPEG, BMP, TIFF
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File uploader - conditional PDF support based on availability
    supported_types = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
    if PDF_SUPPORT:
        supported_types.insert(0, 'pdf')
        file_help_text = "Upload PDF files, images from PDF pages, screenshots, or any image files with dark backgrounds."
        upload_title = "### 📁 Upload PDF or Image Files"
    else:
        file_help_text = "Upload images, screenshots, or any image files with dark backgrounds. PDF support requires PyMuPDF installation."
        upload_title = "### 📁 Upload Image Files"
    
    st.markdown(upload_title)
    uploaded_files = st.file_uploader(
        "Choose files to invert colors",
        type=supported_types,
        accept_multiple_files=True,
        help=file_help_text
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        
        # Categorize files
        pdf_files = [f for f in uploaded_files if f.name.lower().endswith('.pdf')]
        image_files = [f for f in uploaded_files if not f.name.lower().endswith('.pdf')]
        
        if pdf_files:
            st.markdown(f"📄 **PDF Files:** {len(pdf_files)}")
            for pdf_file in pdf_files:
                file_size_mb = pdf_file.size / (1024 * 1024)
                st.write(f"  • {pdf_file.name} ({file_size_mb:.1f} MB)")
        
        if image_files:
            st.markdown(f"🖼️ **Image Files:** {len(image_files)}")
            # Show preview of image files
            if len(image_files) <= 6:
                cols = st.columns(min(len(image_files), 3))
                for i, file in enumerate(image_files):
                    with cols[i % 3]:
                        try:
                            image = Image.open(file)
                            st.image(image, caption=file.name, use_column_width=True)
                            file_size_mb = file.size / (1024 * 1024)
                            st.caption(f"{file_size_mb:.1f} MB")
                        except:
                            st.write(f"📄 {file.name}")
            else:
                for file in image_files:
                    file_size_mb = file.size / (1024 * 1024)
                    st.write(f"  • {file.name} ({file_size_mb:.1f} MB)")
        
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
        
        # PDF-specific options - only show if PDF support is available
        if pdf_files and PDF_SUPPORT:
            st.markdown("### 📄 PDF Processing Options")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                page_naming = st.selectbox(
                    "PDF Page Naming",
                    ["filename_page_1", "filename_p1", "page_1_filename"],
                    help="How to name individual PDF pages"
                )
            
            with col2:
                if len(pdf_files) == 1 and PDF_SUPPORT:
                    # Show page count if single PDF
                    try:
                        pdf_file = pdf_files[0]
                        pdf_file.seek(0)
                        pdf_bytes = pdf_file.read()
                        
                        if PDF_LIBRARY == "pdf2image":
                            from pdf2image import pdfinfo_from_bytes
                            info = pdfinfo_from_bytes(pdf_bytes)
                            page_count = info.get("Pages", "Unknown")
                        elif PDF_LIBRARY == "pymupdf":
                            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            page_count = len(pdf_doc)
                            pdf_doc.close()
                        
                        st.info(f"📄 PDF has {page_count} pages")
                    except Exception as e:
                        st.info("📄 PDF ready for processing")
        
        # Process button
        if st.button("🔄 Process Files & Invert Colors", type="primary", use_container_width=True):
            
            # Progress tracking
            total_operations = len(image_files)
            
            # Count PDF pages for progress
            pdf_page_count = 0
            if pdf_files and PDF_SUPPORT:
                for pdf_file in pdf_files:
                    try:
                        pdf_file.seek(0)
                        pdf_bytes = pdf_file.read()
                        
                        if PDF_LIBRARY == "pdf2image":
                            from pdf2image import pdfinfo_from_bytes
                            info = pdfinfo_from_bytes(pdf_bytes)
                            pdf_page_count += info.get("Pages", 0)
                        elif PDF_LIBRARY == "pymupdf":
                            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            pdf_page_count += len(pdf_doc)
                            pdf_doc.close()
                    except Exception as e:
                        st.warning(f"Could not count pages in {pdf_file.name}: {e}")
                        pass
            
            total_operations += pdf_page_count
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_files = {}
            current_operation = 0
            
            # Process PDF files first - only if PDF support is available
            if pdf_files and PDF_SUPPORT:
                for pdf_file in pdf_files:
                    status_text.text(f"Converting PDF: {pdf_file.name}...")
                    
                    # Get PDF bytes
                    pdf_file.seek(0)
                    pdf_bytes = pdf_file.read()
                    
                    # Convert PDF to images
                    pdf_images = convert_pdf_to_images(pdf_bytes, dpi=dpi_setting)
                    
                    if pdf_images:
                        base_name = Path(pdf_file.name).stem
                        
                        for i, (image, page_name) in enumerate(pdf_images):
                            current_operation += 1
                            progress = current_operation / total_operations
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {pdf_file.name} - {page_name}...")
                            
                            # Process the image
                            inverted_bytes = process_pil_image(image, f"{base_name}_{page_name}")
                            
                            if inverted_bytes:
                                # Generate output filename
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
                                
                                # Generate filename based on naming preference
                                if page_naming == "filename_page_1":
                                    output_filename = f"{base_name}_page_{i+1}{suffix}{ext}"
                                elif page_naming == "filename_p1":
                                    output_filename = f"{base_name}_p{i+1}{suffix}{ext}"
                                else:  # page_1_filename
                                    output_filename = f"page_{i+1}_{base_name}{suffix}{ext}"
                                
                                processed_files[output_filename] = inverted_bytes
            
            # Process image files
            for image_file in image_files:
                current_operation += 1
                progress = current_operation / total_operations
                progress_bar.progress(progress)
                status_text.text(f"Processing image: {image_file.name}...")
                
                # Get file bytes
                image_file.seek(0)
                file_bytes = image_file.read()
                
                # Process the image
                inverted_image = process_image_file(file_bytes, image_file.name)
                
                if inverted_image:
                    # Generate output filename
                    base_name = Path(image_file.name).stem
                    
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
                
                # Use first image file or first PDF page for preview
                preview_image = None
                if image_files:
                    preview_file = image_files[0]
                    preview_file.seek(0)
                    preview_image = Image.open(preview_file)
                elif pdf_files and pdf_images:
                    preview_image = pdf_images[0][0]
                
                if preview_image:
                    inverted_preview = ImageOps.invert(preview_image.convert('RGB'))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Before (Original)**")
                        st.image(preview_image, use_column_width=True)
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
                
                # Show processing summary
                st.markdown("### 📊 Processing Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Files Processed", len(processed_files))
                
                with col2:
                    if pdf_files:
                        st.metric("PDF Pages Converted", pdf_page_count)
                    else:
                        st.metric("Image Files", len(image_files))
                
                with col3:
                    total_size = sum(len(data) for data in processed_files.values())
                    st.metric("Total Size", f"{total_size / (1024*1024):.1f} MB")
                
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
                st.error("❌ No files were successfully processed. Please check your files and try again.")
    
    else:
        # Show upload instructions
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        st.markdown("""
        ### 📤 Ready to Save Ink?
        
        **🆕 Now supports PDF files directly!**
        1. Upload PDF files or images
        2. Automatic PDF-to-image conversion
        3. Color inversion for ink savings
        4. Download processed files
        
        **Perfect for:**
        - 📊 Dark presentation slides (PDF/PowerPoint)
        - 💻 Code screenshots  
        - 📚 Academic papers and documents
        - 🎨 Any dark background content
        - 📄 Multi-page PDF documents
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
