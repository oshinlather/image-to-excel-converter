# Google Sheets Integration Setup Guide 📊

Follow these steps to enable writing extracted data directly to Google Sheets.

## 🔑 Step 1: Create Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google Sheets API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Enable **Google Drive API**:
   - Search for "Google Drive API"
   - Click "Enable"

## 👤 Step 2: Create Service Account Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Service account name**: `imptac-sheets-writer`
   - **Description**: `Service account for writing to Google Sheets`
4. Click "Create and Continue"
5. **Skip** the optional steps (roles and user access)
6. Click "Done"

## 🔐 Step 3: Generate JSON Key

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose **JSON** format
5. Click "Create"
6. A JSON file will download automatically - **Keep this file safe!**

## 📝 Step 4: Configure Streamlit Secrets

### For Local Development:

1. Open (or create) `.streamlit/secrets.toml` in your project
2. Add your service account credentials in this format:

```toml
# Gemini API Key
GEMINI_API_KEY = "your-gemini-api-key"

# Google Sheets Service Account
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**Note:** Copy all values from the downloaded JSON file.

### For Streamlit Cloud:

1. Go to your app on [share.streamlit.io](https://share.streamlit.io/)
2. Click on Settings (⚙️) → "Secrets"
3. Paste the same TOML format content
4. Click "Save"
5. Reboot your app

## 📤 Step 5: Share Your Google Spreadsheet

1. Open your Google Spreadsheet
2. Click "Share" button (top right)
3. **Copy the service account email** from the JSON file:
   - It looks like: `imptac-sheets-writer@your-project.iam.gserviceaccount.com`
4. Paste it in the share dialog
5. Set permission to **"Editor"**
6. Click "Send" (uncheck "Notify people")

## ✅ Step 6: Test the Integration

1. Run your Streamlit app
2. Extract data from an image
3. Enter your Google Spreadsheet URL in the "Write to Google Sheets" section
4. Click "Write to Sheets"
5. Check your spreadsheet - data should appear!

## 🎯 Quick Reference

### Get Your Spreadsheet URL:
Open your Google Sheet and copy the URL from the browser:
```
https://docs.google.com/spreadsheets/d/1abc123xyz/edit
```

### Service Account Email Location:
In the JSON file, look for:
```json
"client_email": "your-service-account@project.iam.gserviceaccount.com"
```

## 🔧 Troubleshooting

### "Credentials not found in secrets"
- Check that `secrets.toml` is in the `.streamlit/` folder
- Verify the JSON format is correct
- Restart the Streamlit app

### "Permission denied" or "Spreadsheet not found"
- Make sure you shared the spreadsheet with the service account email
- Give "Editor" permission, not just "Viewer"
- Check that the spreadsheet URL is correct

### "API not enabled"
- Enable both Google Sheets API and Google Drive API in Cloud Console
- Wait a few minutes for changes to propagate

## 🔒 Security Notes

- **Never** commit `secrets.toml` to git (it's in `.gitignore`)
- **Never** share your service account JSON file publicly
- Service account has access **only** to spreadsheets you explicitly share with it
- You can revoke access anytime by removing the service account from the spreadsheet

## 📚 Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [gspread Documentation](https://docs.gspread.org/)

---

Need help? Check the app's info section or create an issue on GitHub!

