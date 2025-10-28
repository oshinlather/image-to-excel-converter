# Image to Excel Converter 📸📊

A Streamlit web application that extracts text from images using OCR (Optical Character Recognition) and exports it to Excel format.

## Features

- 📤 Upload images (PNG, JPG, JPEG)
- 🔍 Extract text using Tesseract OCR
- 📊 Multiple export formats:
  - Single column (one row per line)
  - Table format (auto-detect columns)
  - Single cell (all text in one cell)
- 🌍 Multi-language support
- 📥 Download extracted data as Excel file
- 📋 Optional metadata inclusion
- 🎨 Clean and intuitive user interface

## Prerequisites

### Install Tesseract OCR

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

3. Upload an image containing text

4. Review the extracted text

5. Choose your preferred export format

6. Download the Excel file

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
- **Tesseract OCR**: Text extraction engine
- **Pandas**: Data manipulation and Excel export
- **Pillow**: Image processing
- **OpenPyXL**: Excel file handling

## License

Free to use for personal and commercial projects.

