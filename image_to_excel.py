import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import io
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Image to Excel Converter",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📸 Image to Excel Converter")
st.markdown("Upload an image and extract text to save it in an Excel file")

# Sidebar for configuration
st.sidebar.header("⚙️ Settings")
language = st.sidebar.selectbox(
    "OCR Language",
    ["eng", "eng+hin", "fra", "deu", "spa"],
    help="Select the language for text recognition"
)

# Instructions
with st.expander("📋 Instructions"):
    st.markdown("""
    1. Upload an image file (PNG, JPG, JPEG)
    2. The app will extract text using OCR
    3. Review the extracted text
    4. Choose how to organize the data
    5. Download the Excel file
    """)

# File uploader
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["png", "jpg", "jpeg"],
    help="Upload an image containing text"
)

if uploaded_file is not None:
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 Uploaded Image")
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        # Image information
        st.info(f"**Image Size:** {image.size[0]} x {image.size[1]} pixels")
    
    with col2:
        st.subheader("📝 Extracted Text")
        
        # Extract text using OCR
        with st.spinner("Extracting text from image..."):
            try:
                # Perform OCR
                extracted_text = pytesseract.image_to_string(image, lang=language)
                
                if extracted_text.strip():
                    # Display extracted text
                    st.text_area(
                        "Raw Text",
                        extracted_text,
                        height=300,
                        help="This is the raw text extracted from the image"
                    )
                    
                    st.success("✅ Text extracted successfully!")
                else:
                    st.warning("⚠️ No text found in the image. Please try another image.")
                    extracted_text = None
                    
            except Exception as e:
                st.error(f"❌ Error during text extraction: {str(e)}")
                st.info("Make sure tesseract is installed on your system")
                extracted_text = None
    
    # If text was extracted, provide Excel export options
    if extracted_text and extracted_text.strip():
        st.divider()
        st.subheader("📊 Export to Excel")
        
        # Choose export format
        export_format = st.radio(
            "Select how to organize the data:",
            ["Single Column (One row per line)", 
             "Table Format (Auto-detect columns)", 
             "Single Cell (All text in one cell)"],
            help="Choose how the extracted text should be structured in Excel"
        )
        
        # Prepare dataframe based on selected format
        if export_format == "Single Column (One row per line)":
            # Split text by lines and create dataframe
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            df = pd.DataFrame(lines, columns=["Extracted Text"])
            
        elif export_format == "Table Format (Auto-detect columns)":
            # Try to detect tabular structure
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            rows = []
            for line in lines:
                # Split by multiple spaces or tabs
                import re
                cols = re.split(r'\s{2,}|\t', line)
                rows.append(cols)
            
            # Find maximum number of columns
            max_cols = max(len(row) for row in rows) if rows else 1
            
            # Pad rows to have same number of columns
            for row in rows:
                while len(row) < max_cols:
                    row.append("")
            
            # Create dataframe
            if rows:
                df = pd.DataFrame(rows[1:] if len(rows) > 1 else rows, 
                                columns=rows[0] if len(rows) > 1 else [f"Column {i+1}" for i in range(max_cols)])
            else:
                df = pd.DataFrame()
                
        else:  # Single Cell
            df = pd.DataFrame([[extracted_text]], columns=["Extracted Text"])
        
        # Preview the dataframe
        st.markdown("**Preview:**")
        st.dataframe(df, use_container_width=True)
        
        # Add metadata option
        add_metadata = st.checkbox("Include metadata (filename, date, etc.)")
        
        if add_metadata:
            metadata_df = pd.DataFrame({
                "Metadata": ["Source File", "Extraction Date", "Image Size"],
                "Value": [
                    uploaded_file.name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    f"{image.size[0]} x {image.size[1]}"
                ]
            })
            st.markdown("**Metadata to include:**")
            st.dataframe(metadata_df, use_container_width=True)
        
        # Create Excel file in memory
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Extracted Data', index=False)
            
            if add_metadata:
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        excel_data = output.getvalue()
        
        # Download button
        st.download_button(
            label="📥 Download Excel File",
            data=excel_data,
            file_name=f"extracted_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    # Show placeholder when no file is uploaded
    st.info("👆 Please upload an image file to get started")
    
    # Sample image placeholder
    st.markdown("---")
    st.markdown("### 💡 Tips for best results:")
    st.markdown("""
    - Use high-resolution images with clear text
    - Ensure good contrast between text and background
    - Avoid blurry or rotated images
    - For better accuracy, crop the image to contain only the text area
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Made with ❤️ using Streamlit | Powered by Tesseract OCR
    </div>
    """,
    unsafe_allow_html=True
)

