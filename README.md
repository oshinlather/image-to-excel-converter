# Invoice to Excel Converter 📄✨

A beautiful, modern Streamlit web application that extracts invoice/table data from images using AI and exports it to Excel format with an editable interface.

## Features

### 🎨 Modern UI Design
- **Dark theme** with clean, professional interface
- **Two-panel layout**: Upload on left, editable table on right
- **Drag & drop** file upload support
- **Real-time preview** of uploaded invoices

### 🤖 AI-Powered Extraction
- **Gemini 2.5 Flash AI** for superior accuracy
- Automatically detects table structure, headers, and data
- Handles complex invoice layouts
- Supports invoices, bills, forms, and any tabular data

### ✏️ Interactive Data Editing
- **Editable table** - modify any cell directly in browser
- **Add/remove rows** dynamically
- **Column types**: Numbers, text, formatted currency
- **Real-time calculations** for totals
- **Clear all** to start fresh

### 📊 Smart Features
- **Live summary metrics**: Total items, quantities, grand total
- **Auto-numbering** for S.No. column
- **Formatted output** with proper data types
- **One-click Excel export** with timestamp

### 🔒 Secure & Private
- API key stored locally (never pushed to GitHub)
- All processing happens client-side
- No data stored on servers

## Prerequisites

### Get Your Free Gemini API Key 🔑

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key
5. Paste it in the app (top right corner)

**Why Gemini AI?**
- ✨ Superior accuracy for invoice/table extraction
- 🧠 Understands complex layouts and handwriting
- 🚀 No local installation required
- 💯 Free tier available (60 requests/minute)

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Local Development

1. **Run the Streamlit app:**
```bash
streamlit run image_to_excel.py
```

2. **Open your browser** (auto-opens) at `http://localhost:8501`

3. **Enter your Gemini API key** in the top-right field

4. **Upload an invoice/image:**
   - Drag & drop into the upload area, OR
   - Click to browse and select a file
   - Supports: JPG, PNG, PDF

5. **Click "Extract Data"** to process with AI

6. **Edit the extracted table:**
   - Click any cell to edit
   - Add rows with the "Add Row" button
   - Delete rows using the table controls
   - Modify quantities, rates, totals

7. **Download Excel** with one click - file includes all your edits!

### Deploy to Streamlit Cloud

1. Push your code to GitHub (this repository includes the necessary `packages.txt` file)

2. Go to [share.streamlit.io](https://share.streamlit.io/)

3. Sign in with GitHub

4. Click "New app" and select:
   - Repository: `oshinlather/image-to-excel-converter`
   - Branch: `main`
   - Main file path: `image_to_excel.py`

5. Click "Deploy"!

**Note:** The `packages.txt` file in this repository ensures Tesseract OCR is installed automatically on Streamlit Cloud.

## Tips for Best Results

- Use high-resolution images with clear text
- Ensure good contrast between text and background
- Avoid blurry or rotated images
- For better accuracy, crop images to contain only the text area

## Supported Languages

The app supports multiple OCR languages:
- English
- English + Hindi
- French
- German
- Spanish

You can add more languages by installing additional Tesseract language packs.

## Troubleshooting

**Error: "tesseract is not installed"**
- Make sure Tesseract OCR is installed on your system (see Prerequisites)
- On Windows, you may need to add Tesseract to your PATH

**No text extracted from image**
- Check image quality and text clarity
- Try adjusting the image contrast
- Ensure the selected language matches the text in the image

## Technologies Used

- **Streamlit**: Web application framework
- **Google Gemini AI**: Advanced AI-powered table extraction
- **Tesseract OCR**: Alternative text extraction engine
- **Pandas**: Data manipulation and Excel export
- **Pillow**: Image processing
- **OpenCV**: Image preprocessing
- **OpenPyXL**: Excel file handling

## License

Free to use for personal and commercial projects.

