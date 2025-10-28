# Image to Excel Converter 📸📊

A Streamlit web application that extracts text from images using OCR (Optical Character Recognition) and exports it to Excel format.

## Features

- 📤 Upload images (PNG, JPG, JPEG)
- 🤖 **NEW: Gemini AI extraction (Recommended)** - Superior accuracy for tables
- 🔍 Alternative: Tesseract OCR for text extraction
- 📊 Multiple export formats:
  - Smart table detection with AI
  - Single column (one row per line)
  - Table format (auto-detect columns)
  - Manual table configuration
  - Single cell (all text in one cell)
- 🌍 Multi-language support
- 📥 Download extracted data as Excel file
- 📋 Optional metadata inclusion
- ✏️ Editable column headers
- 🎨 Clean and intuitive user interface

## Prerequisites

### Option 1: Gemini AI (Recommended) 🤖

Get a **free** Gemini API key for best results:

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key
5. Enter it in the app sidebar when using Gemini extraction

**Why Gemini?**
- Much better accuracy for table extraction
- Understands complex layouts
- No local installation needed
- Free tier available

### Option 2: Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Local Development

1. Run the Streamlit app:
```bash
streamlit run image_to_excel.py
```

2. Open your browser (it should open automatically) to `http://localhost:8501`

3. **Choose extraction method in sidebar:**
   - **Gemini AI (Recommended):** Enter your API key for best results
   - **Tesseract OCR:** Uses local OCR (requires Tesseract installation)

4. Upload an image containing text or a table

5. Review the extracted data

6. Customize column headers if needed

7. Download the Excel file

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

