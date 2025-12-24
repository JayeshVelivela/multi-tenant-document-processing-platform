# How to Access Your Document Data

You have **2 documents** with extracted metadata! Here are all the ways to access your data:

## 🌐 Via Web Interface

### 1. Dashboard
- **URL**: `http://localhost:5173/dashboard` (or your frontend URL)
- **What you see**: Summary statistics (total, pending, processing, completed)
- **Auto-refreshes**: Every 5 seconds

### 2. Documents Page
- **URL**: `http://localhost:5173/documents`
- **What you can do**:
  - View all documents with full metadata
  - Filter by status (all, pending, processing, completed, failed)
  - Download original files (📥 Download button)
  - **Export all data** (📥 Export JSON or 📊 Export CSV buttons)
  - See extracted entities (dates, amounts, companies)
  - View text preview

## 🔌 Via API

### Get Your Auth Token
1. Login via web interface or API:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'
```

2. Copy the `access_token` from the response

### API Endpoints

#### 1. List All Documents
```bash
curl -X GET "http://localhost:8000/api/v1/documents/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2. Get Specific Document
```bash
curl -X GET "http://localhost:8000/api/v1/documents/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. Export as JSON
```bash
curl -X GET "http://localhost:8000/api/v1/documents/export/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o documents.json
```

#### 4. Export as CSV
```bash
curl -X GET "http://localhost:8000/api/v1/documents/export/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o documents.csv
```

#### 5. Download Original File
```bash
curl -X GET "http://localhost:8000/api/v1/documents/1/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o downloaded_file.pdf
```

## 📊 Interactive API Documentation

Visit: **http://localhost:8000/docs**

- Interactive API explorer
- Test endpoints directly
- See request/response examples
- No need to write curl commands!

## 🐍 Python Script Example

```python
import requests
import json

# Login
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "your@email.com", "password": "yourpassword"}
)
token = login_response.json()["access_token"]

# Get all documents
headers = {"Authorization": f"Bearer {token}"}
docs_response = requests.get(
    "http://localhost:8000/api/v1/documents/",
    headers=headers
)
documents = docs_response.json()["items"]

# Print metadata
for doc in documents:
    print(f"\n📄 {doc['original_filename']}")
    print(f"   Status: {doc['status']}")
    if doc.get('extracted_metadata'):
        meta = doc['extracted_metadata']
        print(f"   Type: {meta.get('document_type', 'N/A')}")
        print(f"   Pages: {meta.get('page_count', 'N/A')}")
        print(f"   Words: {meta.get('word_count', 'N/A')}")
        if meta.get('entities'):
            print(f"   Dates: {', '.join(meta['entities'].get('dates', []))}")
            print(f"   Amounts: {', '.join(meta['entities'].get('amounts', []))}")
            print(f"   Companies: {', '.join(meta['entities'].get('companies', []))}")

# Export to JSON
export_response = requests.get(
    "http://localhost:8000/api/v1/documents/export/json",
    headers=headers
)
with open('my_documents.json', 'w') as f:
    json.dump(export_response.json(), f, indent=2)
print("\n✅ Exported to my_documents.json")
```

## 📋 What Data is Available?

For each document, you can access:

### Basic Info
- Document ID
- Original filename
- File size
- MIME type
- Status (pending, processing, completed, failed)
- Upload date
- Processing date

### Extracted Metadata
- **Document Type**: invoice, receipt, contract, report, letter, document
- **Page Count**: Number of pages
- **Word Count**: Total words
- **Language**: Detected language code (en, es, fr, etc.)

### Extracted Entities
- **Dates**: All dates found (YYYY-MM-DD, MM/DD/YYYY, etc.)
- **Amounts**: Currency amounts ($1,234.56, USD 500, etc.)
- **Companies**: Organization names

### Text Content
- **Text Preview**: First 200 characters
- **Full Text**: Complete extracted text (in database)

## 🎯 Quick Access Methods

### Method 1: Web Interface (Easiest)
1. Go to `http://localhost:5173/documents`
2. Click "📊 Export CSV" or "📥 Export JSON"
3. File downloads automatically!

### Method 2: API Docs (Interactive)
1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button
3. Enter your token
4. Test any endpoint!

### Method 3: Command Line
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}' \
  | jq -r '.access_token')

# Export data
curl -X GET "http://localhost:8000/api/v1/documents/export/json" \
  -H "Authorization: Bearer $TOKEN" \
  -o my_data.json
```

## 🔍 Your Current Data

Based on the database, you have:
- **2 documents** total
- **2 completed** documents with metadata
- Both documents have extracted metadata including:
  - Document types
  - Page counts
  - Word counts
  - And more!

## 💡 Next Steps

1. **View in Web**: Go to Documents page to see all metadata
2. **Export Data**: Use Export buttons to download JSON/CSV
3. **Use API**: Integrate with your own scripts or tools
4. **Explore**: Check out `/docs` for full API documentation

---

**Need help?** Check `DATA_ACCESS_GUIDE.md` for more detailed information and use cases!

