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
import gspread
from google.oauth2.service_account import Credentials

# Helper function to evaluate math expressions
def calculate_expression(value):
    """Calculate mathematical expressions like '50+5' -> 55"""
    if pd.isna(value):
        return value
    
    # Convert to string and clean
    value_str = str(value).strip()
    
    # Check if it contains math operators
    if any(op in value_str for op in ['+', '-', '*', '/']):
        try:
            # Safely evaluate the expression
            result = eval(value_str, {"__builtins__": {}}, {})
            return result
        except:
            return value
    
    return value

# Helper functions for Google Sheets integration
def connect_to_google_sheets():
    """Connect to Google Sheets using service account credentials"""
    try:
        # Try to get credentials from Streamlit secrets
        if not hasattr(st, 'secrets'):
            return None, "Streamlit secrets not available"
        
        if 'gcp_service_account' not in st.secrets:
            available_keys = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else []
            return None, f"gcp_service_account not found in secrets. Available keys: {available_keys}"
        
        credentials = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        return client, None
    except Exception as e:
        import traceback
        return None, f"Failed to connect to Google Sheets: {str(e)}\n{traceback.format_exc()}"

def write_to_google_sheet(client, spreadsheet_url, df, sheet_name="Sheet1"):
    """Write dataframe to Google Sheets"""
    try:
        # Open the spreadsheet
        spreadsheet = client.open_by_url(spreadsheet_url)
        
        # Try to get the worksheet, create if doesn't exist
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
        
        # Clear existing data
        worksheet.clear()
        
        # Convert dataframe to list of lists
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Write data to sheet
        worksheet.update('A1', data)
        
        return True, None
    except Exception as e:
        return False, f"Failed to write to Google Sheets: {str(e)}"

# Set page configuration with dark theme
st.set_page_config(
    page_title="Invoice to Excel Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #1a1a1a;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Upload section */
    .upload-section {
        background-color: #2a2a2a;
        border: 2px dashed #555;
        border-radius: 15px;
        padding: 60px 40px;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Table styling */
    .dataframe {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    /* Download button */
    .download-btn {
        background-color: #2196F3;
        color: white;
        padding: 12px 30px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        margin-top: 20px;
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background-color: #333;
        color: white;
        border: 1px solid #555;
        border-radius: 5px;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* Data editor */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for Gemini extraction
def extract_table_with_gemini(image, api_key):
    """Extract table data using Google Gemini Vision API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = """
        Analyze this invoice/form image and extract ALL data in a structured table format.
        
        Instructions:
        1. Identify all column headers (like S.No., Item, Quantity, Unit, Rate, Total, etc.)
        2. Extract ALL rows of data
        3. Maintain exact text and numbers as they appear
        4. Return data as JSON:
        {
            "headers": ["S.No.", "Food Item", "Quantity", "Unit", "Rate", "Total"],
            "rows": [
                ["1", "Item Name", "10", "kg", "100", "1000"],
                ["2", "Item Name 2", "5", "ltr", "50", "250"]
            ]
        }
        
        Important:
        - Extract EVERY row visible
        - Use empty string "" for missing cells
        - Preserve exact text
        - Return ONLY JSON, no other text
        """
        
        response = model.generate_content([prompt, image])
        response_text = response.text.strip()
        
        if response_text.startswith('```'):
            response_text = re.sub(r'^```json?\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        
        data = json.loads(response_text)
        
        if 'headers' in data and 'rows' in data:
            df = pd.DataFrame(data['rows'], columns=data['headers'])
            return df, None
        else:
            return None, "Invalid response format from Gemini"
            
    except json.JSONDecodeError as e:
        return None, f"Failed to parse response: {str(e)}"
    except Exception as e:
        return None, f"Gemini API error: {str(e)}"

# Get API key
if 'api_key' not in st.session_state:
    default_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, 'secrets') else ""
    st.session_state.api_key = default_key

# Initialize session state for dataframe
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        'S.No.': [1],
        'Food Item': [''],
        'Unit': [''],
        'Required Qty': ['']
    })

# Header
col1, col2 = st.columns([1, 3])
with col1:
    st.title("📄 Invoice Extractor")
with col2:
    # API Key input (top right)
    api_key = st.text_input("🔑 Gemini API Key", 
                            value=st.session_state.api_key,
                            type="password",
                            placeholder="Enter your API key",
                            help="Get free key from https://aistudio.google.com/app/apikey")
    if api_key:
        st.session_state.api_key = api_key

st.markdown("---")

# Two column layout
col_left, col_right = st.columns([1, 1.5], gap="large")

# LEFT COLUMN - Upload Section
with col_left:
    st.markdown("### 📤 Upload Invoice")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Supports JPG, PNG, PDF",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption="Uploaded Invoice")
        
        # Extract button
        if st.button("🚀 Extract Data", use_container_width=True, type="primary"):
            if not st.session_state.api_key:
                st.error("❌ Please enter your Gemini API key above")
            else:
                with st.spinner("🔍 Extracting data from invoice..."):
                    df, error = extract_table_with_gemini(image, st.session_state.api_key)
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        # Process extracted data - calculate any math expressions
                        if 'Quantity' in df.columns:
                            df['Quantity'] = df['Quantity'].apply(calculate_expression)
                        if 'Required Qty' in df.columns:
                            df['Required Qty'] = df['Required Qty'].apply(calculate_expression)
                        
                        st.session_state.df = df
                        
                        # Store sync status in session state
                        st.session_state.extraction_complete = True
                        st.session_state.sync_attempted = False
                        
                        # Auto-sync to Google Sheets if configured
                        has_secrets = hasattr(st, 'secrets')
                        has_url = 'GOOGLE_SHEET_URL' in st.secrets if has_secrets else False
                        
                        if has_secrets and has_url:
                            sheet_url = st.secrets.get('GOOGLE_SHEET_URL', '')
                            sheet_name = st.secrets.get('GOOGLE_SHEET_NAME', 'Sheet1')
                            
                            if sheet_url and sheet_url != 'YOUR_SPREADSHEET_URL_HERE':
                                try:
                                    client, sync_error = connect_to_google_sheets()
                                    
                                    if not sync_error:
                                        success, write_error = write_to_google_sheet(client, sheet_url, df, sheet_name)
                                        
                                        if success:
                                            st.session_state.sync_status = "success"
                                            st.session_state.sync_message = f"Auto-synced to Google Sheets: {sheet_name}"
                                        else:
                                            st.session_state.sync_status = "error"
                                            st.session_state.sync_message = f"Write failed: {write_error}"
                                    else:
                                        st.session_state.sync_status = "error"
                                        st.session_state.sync_message = f"Connection error: {sync_error}"
                                except Exception as e:
                                    st.session_state.sync_status = "error"
                                    st.session_state.sync_message = f"Exception: {str(e)}"
                                
                                st.session_state.sync_attempted = True
                        
                        st.rerun()
    else:
        # Upload placeholder
        st.markdown("""
        <div class="upload-section">
            <h3>☁️ Drag & drop your invoice here</h3>
            <p style="color: #999;">or click to browse</p>
            <p style="color: #666; font-size: 14px; margin-top: 20px;">Supports JPG, PNG, PDF</p>
        </div>
        """, unsafe_allow_html=True)

# RIGHT COLUMN - Extracted Data
with col_right:
    st.markdown("### 📊 Extracted Data")
    
    # Debug: Show what secrets are available
    if hasattr(st, 'secrets'):
        available_keys = list(st.secrets.keys())
        st.info(f"🔍 Debug: Available secrets keys: {available_keys}")
    else:
        st.error("❌ Debug: st.secrets is not available!")
    
    # Show sync status if extraction was completed
    if hasattr(st.session_state, 'extraction_complete') and st.session_state.extraction_complete:
        if hasattr(st.session_state, 'sync_attempted') and st.session_state.sync_attempted:
            if st.session_state.get('sync_status') == 'success':
                st.success(f"✅ {st.session_state.get('sync_message', 'Synced successfully')}")
            elif st.session_state.get('sync_status') == 'error':
                st.error(f"❌ {st.session_state.get('sync_message', 'Sync failed')}")
        st.session_state.extraction_complete = False
    
    # Info message about auto-calculation
    st.info("💡 **Tip:** Type math expressions like '50+5' in quantity fields - they'll auto-calculate!", icon="✨")
    
    # Show editable dataframe
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "S.No.": st.column_config.NumberColumn("S.No.", width="small"),
            "Food Item": st.column_config.TextColumn("Food Item", width="large"),
            "Unit": st.column_config.TextColumn("Unit", width="medium"),
            "Required Qty": st.column_config.TextColumn("Required Qty", width="medium", help="Auto-calculates: 50+5 = 55"),
            "Quantity": st.column_config.TextColumn("Quantity", width="medium", help="Auto-calculates: 50+5 = 55") if "Quantity" in st.session_state.df.columns else None,
            "Rate": st.column_config.NumberColumn("Rate", width="medium", format="%.2f") if "Rate" in st.session_state.df.columns else None,
            "Total": st.column_config.NumberColumn("Total", width="medium", format="%.2f") if "Total" in st.session_state.df.columns else None
        },
        hide_index=True,
        height=400
    )
    
    # Process edited data - automatically calculate math expressions in quantity columns
    if 'Quantity' in edited_df.columns:
        edited_df['Quantity'] = edited_df['Quantity'].apply(calculate_expression)
    if 'Required Qty' in edited_df.columns:
        edited_df['Required Qty'] = edited_df['Required Qty'].apply(calculate_expression)
    
    # Update session state
    st.session_state.df = edited_df
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("➕ Add Row", use_container_width=True):
            # Create new row with same columns as current df
            new_row_data = {'S.No.': len(st.session_state.df) + 1}
            for col in st.session_state.df.columns:
                if col != 'S.No.':
                    new_row_data[col] = '' if col in ['Food Item', 'Unit', 'Required Qty'] else 0
            
            new_row = pd.DataFrame([new_row_data])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.rerun()
    
    with col_btn2:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.df = pd.DataFrame({
                'S.No.': [1],
                'Food Item': [''],
                'Unit': [''],
                'Required Qty': ['']
            })
            st.rerun()
    
    with col_btn3:
        # Export to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.df.to_excel(writer, sheet_name='Invoice Data', index=False)
        
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    
    # Google Sheets Integration - Only show if NOT auto-configured
    default_sheet_url = st.secrets.get('GOOGLE_SHEET_URL', '') if hasattr(st, 'secrets') else ''
    default_sheet_name = st.secrets.get('GOOGLE_SHEET_NAME', 'Sheet1') if hasattr(st, 'secrets') else 'Sheet1'
    auto_sync_enabled = default_sheet_url and default_sheet_url != 'YOUR_SPREADSHEET_URL_HERE'
    
    # Only show manual controls if auto-sync is NOT configured
    if not auto_sync_enabled:
        st.markdown("---")
        st.markdown("### 📊 Write to Google Sheets")
        st.info("💡 Configure `GOOGLE_SHEET_URL` in secrets for automatic sync!")
        
        # Spreadsheet URL input
        spreadsheet_url = st.text_input(
            "Google Spreadsheet URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste the full URL of your Google Spreadsheet"
        )
        
        # Sheet name input
        col_sheet1, col_sheet2 = st.columns([2, 1])
        with col_sheet1:
            sheet_name = st.text_input(
                "Sheet Name",
                value="Sheet1",
                help="Name of the sheet to write data to"
            )
        
        with col_sheet2:
            if st.button("📤 Write to Sheets", use_container_width=True, type="secondary"):
                if not spreadsheet_url:
                    st.error("❌ Please enter a Google Spreadsheet URL")
                else:
                    with st.spinner("Writing to Google Sheets..."):
                        client, error = connect_to_google_sheets()
                        
                        if error:
                            st.error(f"❌ {error}")
                            st.info("""
                            **Setup Required:**
                            1. Create Google Service Account credentials
                            2. Add credentials to Streamlit secrets
                            3. Share your spreadsheet with the service account email
                            
                            See instructions below for details.
                            """)
                        else:
                            success, write_error = write_to_google_sheet(
                                client, 
                                spreadsheet_url, 
                                st.session_state.df, 
                                sheet_name
                            )
                            
                            if success:
                                st.success(f"✅ Successfully written to Google Sheets: {sheet_name}")
                            else:
                                st.error(f"❌ {write_error}")
    
    # Summary
    if len(st.session_state.df) > 0:
        st.markdown("---")
        
        # Dynamic summary based on available columns
        if 'Total' in st.session_state.df.columns:
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            
            with col_sum1:
                st.metric("Total Items", len(st.session_state.df))
            with col_sum2:
                # Check for either Quantity or Required Qty column
                if 'Required Qty' in st.session_state.df.columns:
                    total_qty = pd.to_numeric(st.session_state.df['Required Qty'], errors='coerce').sum()
                    st.metric("Total Required Qty", f"{total_qty:.0f}")
                elif 'Quantity' in st.session_state.df.columns:
                    total_qty = pd.to_numeric(st.session_state.df['Quantity'], errors='coerce').sum()
                    st.metric("Total Quantity", f"{total_qty:.0f}")
            with col_sum3:
                total_amount = st.session_state.df['Total'].sum() if 'Total' in st.session_state.df else 0
                st.metric("Grand Total", f"₹{total_amount:.2f}")
        else:
            # Simple summary for food demand forms
            col_sum1, col_sum2 = st.columns(2)
            
            with col_sum1:
                st.metric("Total Items", len(st.session_state.df))
            with col_sum2:
                if 'Required Qty' in st.session_state.df.columns:
                    # Count non-empty items
                    filled_items = st.session_state.df['Required Qty'].astype(str).str.strip().ne('').sum()
                    st.metric("Items with Quantity", filled_items)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Powered by <strong>Google Gemini AI</strong> ✨ | Made with ❤️ using Streamlit</p>
    <p style='font-size: 12px; margin-top: 10px;'>Get your free API key: 
    <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color: #4CAF50;'>Google AI Studio</a></p>
</div>
""", unsafe_allow_html=True)
