import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import io
from datetime import datetime
import re
import cv2
import numpy as np
import google.generativeai as genai
import json

# Helper functions for image preprocessing and table extraction
def preprocess_image(image):
    """Preprocess image for better OCR results"""
    # Convert PIL Image to OpenCV format
    img_array = np.array(image)
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Apply thresholding to get better contrast
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh)
    
    # Convert back to PIL Image
    return Image.fromarray(denoised)

def extract_table_data(text):
    """Extract table data from OCR text"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Try to identify header and data rows
    table_data = []
    headers = []
    
    # Look for common table patterns
    for i, line in enumerate(lines):
        # Skip very short lines or numbers-only lines at the beginning
        if len(line) < 3 or (line.isdigit() and i < 5):
            continue
            
        # Identify potential headers (lines with words like "Item", "Qty", "Unit", etc.)
        if any(keyword in line.lower() for keyword in ['item', 'qty', 'quantity', 'unit', 'name', 'description']):
            # Try to split into columns
            parts = re.split(r'\s{2,}|\t', line)
            if len(parts) > 1:
                headers.extend(parts)
        else:
            # Try to extract data rows
            # Split by multiple spaces or tabs
            parts = re.split(r'\s{2,}|\t', line)
            if len(parts) > 1 or any(c.isalnum() for c in line):
                table_data.append(line)
    
    return headers, table_data

def smart_parse_to_dataframe(text):
    """Intelligently parse text into a structured dataframe"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Remove very short lines and clean up
    cleaned_lines = []
    for line in lines:
        # Remove excessive spaces
        line = re.sub(r'\s+', ' ', line)
        if len(line) > 2 and not line.replace('.', '').replace('-', '').replace('_', '').strip() == '':
            cleaned_lines.append(line)
    
    # Try to identify table structure
    data_rows = []
    header_found = False
    potential_headers = []
    
    for i, line in enumerate(cleaned_lines):
        # Split by multiple spaces, tabs, or special delimiters
        parts = re.split(r'\s{2,}|\t|\|', line)
        parts = [p.strip() for p in parts if p.strip()]
        
        # Look for header indicators
        if not header_found and any(keyword in line.lower() for keyword in 
                                     ['item', 'name', 'qty', 'quantity', 'unit', 'description', 'product']):
            potential_headers = parts
            header_found = True
            continue
        
        # If we have multiple parts, it's likely a data row
        if len(parts) >= 2:
            data_rows.append(parts)
        elif len(parts) == 1 and header_found:
            # Single item might be a row item, add empty columns
            data_rows.append([parts[0], '', ''])
    
    # If no clear headers found, create generic ones
    if not potential_headers and data_rows:
        max_cols = max(len(row) for row in data_rows)
        potential_headers = [f'Column {i+1}' for i in range(max_cols)]
    
    # Ensure all rows have the same number of columns
    if data_rows and potential_headers:
        max_cols = len(potential_headers)
        for row in data_rows:
            while len(row) < max_cols:
                row.append('')
            if len(row) > max_cols:
                row = row[:max_cols]
    
    # Create dataframe
    if data_rows:
        df = pd.DataFrame(data_rows, columns=potential_headers if potential_headers else None)
        return df
    else:
        # Fallback: one column with all text
        return pd.DataFrame(cleaned_lines, columns=['Extracted Text'])

def extract_table_with_gemini(image, api_key):
    """Extract table data using Google Gemini Vision API"""
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt for table extraction
        prompt = """
        Analyze this image and extract ALL data in a structured table format.
        
        Instructions:
        1. Identify all column headers (like Item, Quantity, Unit, Price, etc.)
        2. Extract ALL rows of data
        3. Maintain the exact text and numbers as they appear
        4. Return the data as a JSON object with this structure:
        {
            "headers": ["Column1", "Column2", "Column3"],
            "rows": [
                ["value1", "value2", "value3"],
                ["value1", "value2", "value3"]
            ]
        }
        
        Important:
        - Extract EVERY row visible in the image
        - If a cell is empty, use an empty string ""
        - Preserve all text exactly as shown
        - Don't skip any data
        - Return ONLY the JSON, no other text
        """
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        # Parse JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = re.sub(r'^```json?\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        
        # Parse JSON
        data = json.loads(response_text)
        
        # Create DataFrame
        if 'headers' in data and 'rows' in data:
            df = pd.DataFrame(data['rows'], columns=data['headers'])
            return df, None
        else:
            return None, "Invalid response format from Gemini"
            
    except json.JSONDecodeError as e:
        return None, f"Failed to parse Gemini response: {str(e)}\n\nResponse was: {response_text[:500]}"
    except Exception as e:
        return None, f"Gemini API error: {str(e)}"

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

# Extraction method selection
extraction_method = st.sidebar.radio(
    "Extraction Method",
    ["🤖 Gemini AI (Recommended)", "📝 Tesseract OCR"],
    help="Gemini AI provides much better accuracy for tables"
)

# API Key input for Gemini
if extraction_method == "🤖 Gemini AI (Recommended)":
    gemini_api_key = st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        help="Get your free API key from https://makersuite.google.com/app/apikey"
    )
    
    if not gemini_api_key:
        st.sidebar.warning("⚠️ Please enter your Gemini API key")
        st.sidebar.markdown("[Get free API key →](https://makersuite.google.com/app/apikey)")
else:
    gemini_api_key = None
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
        st.subheader("📝 Extracted Data")
        
        # Check if using Gemini and API key is provided
        if extraction_method == "🤖 Gemini AI (Recommended)" and not gemini_api_key:
            st.warning("⚠️ Please enter your Gemini API key in the sidebar to extract data")
            extracted_text = None
            gemini_df = None
        else:
            # Extract data
            with st.spinner("Extracting data from image..."):
                try:
                    if extraction_method == "🤖 Gemini AI (Recommended)":
                        # Use Gemini for extraction
                        gemini_df, error = extract_table_with_gemini(image, gemini_api_key)
                        
                        if error:
                            st.error(f"❌ {error}")
                            extracted_text = None
                            gemini_df = None
                        else:
                            st.success("✅ Data extracted successfully with Gemini AI!")
                            st.markdown("**Extracted Table:**")
                            st.dataframe(gemini_df, use_container_width=True)
                            extracted_text = "gemini_extracted"  # Flag for later processing
                    else:
                        # Use Tesseract OCR
                        gemini_df = None
                        
                        # Image preprocessing option
                        use_preprocessing = st.checkbox(
                            "🔧 Use image preprocessing (improves OCR accuracy)",
                            value=True,
                            help="Applies grayscale conversion, thresholding, and denoising"
                        )
                        
                        # Preprocess image if selected
                        processed_image = preprocess_image(image) if use_preprocessing else image
                        
                        # Perform OCR with table detection
                        extracted_text = pytesseract.image_to_string(
                            processed_image, 
                            lang=language,
                            config='--psm 6'  # Assume uniform block of text
                        )
                        
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
                    st.error(f"❌ Error during extraction: {str(e)}")
                    if extraction_method == "📝 Tesseract OCR":
                        st.info("Make sure tesseract is installed on your system")
                    extracted_text = None
                    gemini_df = None
    
    # If text was extracted, provide Excel export options
    if extracted_text and extracted_text.strip():
        st.divider()
        st.subheader("📊 Export to Excel")
        
        # If using Gemini, use the extracted dataframe directly
        if extraction_method == "🤖 Gemini AI (Recommended)" and gemini_df is not None:
            df = gemini_df.copy()
            
            # Allow editing headers
            st.markdown("**Customize Column Headers (optional):**")
            col_count = len(df.columns)
            new_headers = []
            
            cols = st.columns(min(col_count, 4))
            for i, col_name in enumerate(df.columns):
                with cols[i % 4]:
                    new_header = st.text_input(
                        f"Column {i+1}",
                        value=str(col_name),
                        key=f"gemini_header_{i}"
                    )
                    new_headers.append(new_header if new_header else f"Column {i+1}")
            
            df.columns = new_headers
            
        else:
            # Tesseract OCR - show format options
            export_format = st.radio(
                "Select how to organize the data:",
                ["Smart Table Detection (Recommended)", 
                 "Single Column (One row per line)", 
                 "Manual Table Format", 
                 "Single Cell (All text in one cell)"],
                help="Choose how the extracted text should be structured in Excel"
            )
            
            # Prepare dataframe based on selected format
            if export_format == "Smart Table Detection (Recommended)":
                # Use intelligent parsing
                df = smart_parse_to_dataframe(extracted_text)
                
                # Allow manual editing of headers
                st.markdown("**Customize Column Headers:**")
                col_count = len(df.columns)
                new_headers = []
                
                cols = st.columns(min(col_count, 4))
                for i, col_name in enumerate(df.columns):
                    with cols[i % 4]:
                        new_header = st.text_input(
                            f"Column {i+1}",
                            value=str(col_name),
                            key=f"header_{i}"
                        )
                        new_headers.append(new_header if new_header else f"Column {i+1}")
                
                df.columns = new_headers
                
            elif export_format == "Single Column (One row per line)":
                # Split text by lines and create dataframe
                lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                df = pd.DataFrame(lines, columns=["Extracted Text"])
                
            elif export_format == "Manual Table Format":
                # Manual column configuration
                st.markdown("**Configure Table Structure:**")
                num_columns = st.number_input("Number of columns", min_value=1, max_value=10, value=3)
                
                # Get column headers
                header_cols = st.columns(num_columns)
                headers = []
                for i in range(num_columns):
                    with header_cols[i]:
                        header = st.text_input(f"Header {i+1}", value=f"Column {i+1}", key=f"manual_header_{i}")
                        headers.append(header)
                
                # Try to detect tabular structure
                lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                rows = []
                for line in lines:
                    # Split by multiple spaces or tabs
                    cols = re.split(r'\s{2,}|\t', line)
                    # Adjust to match number of columns
                    while len(cols) < num_columns:
                        cols.append("")
                    if len(cols) > num_columns:
                        cols = cols[:num_columns]
                    rows.append(cols)
                
                # Create dataframe
                if rows:
                    df = pd.DataFrame(rows, columns=headers)
                else:
                    df = pd.DataFrame(columns=headers)
                    
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

