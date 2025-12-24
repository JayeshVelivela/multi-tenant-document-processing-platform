# Multi Tenant Document Processing Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A production-grade, multi-tenant document processing platform that demonstrates enterprise-level backend engineering practices. Built with FastAPI, PostgreSQL, and Redis, this system showcases real-world software engineering skills suitable for SWE internship and new grad positions.

## 🌟 What This Project Does

This platform allows **multiple companies (tenants)** to securely upload documents, process them asynchronously, and extract structured metadata. Think of it as a simplified version of services like:

- **DocuSign** - Document processing and analysis
- **Dropbox Business** - Multi-tenant file storage with metadata
- **AWS Textract** - Document text and data extraction
- **Invoice2go** - Invoice processing and data extraction

### Why Extract Metadata?

Metadata extraction transforms unstructured documents into searchable, queryable data. Here are real-world use cases:

#### 📄 **Invoice Processing**
- Extract: Amounts, dates, vendor names, line items
- Use case: Automate accounts payable, expense tracking, financial reporting
- Example: Upload an invoice → Get structured data → Auto-populate accounting system

#### 📋 **Contract Analysis**
- Extract: Key dates, parties, terms, obligations
- Use case: Legal document review, contract management, compliance tracking
- Example: Upload contract → Extract expiration dates → Set reminders

#### 📝 **Form Processing**
- Extract: Filled fields, signatures, dates
- Use case: Application processing, survey analysis, data entry automation
- Example: Upload application form → Extract applicant info → Populate database

#### 🔍 **Document Search & Discovery**
- Extract: Full text, keywords, entities
- Use case: Make documents searchable, content discovery, knowledge management
- Example: Upload documents → Extract text → Enable full-text search

#### 📊 **Compliance & Auditing**
- Extract: Regulated information, dates, amounts
- Use case: Regulatory compliance, audit trails, financial reporting
- Example: Upload financial documents → Extract amounts → Generate reports

#### 🤖 **Automation & Integration**
- Extract: Structured data from unstructured documents
- Use case: Integrate with other systems, automate workflows, reduce manual work
- Example: Upload receipt → Extract expense data → Send to accounting software

**In this demo**, the system extracts:
- Page count, word count, language
- Document type (invoice, contract, etc.)
- Extracted text preview
- Entities (dates, amounts, company names)

## 🚀 Features

### ✅ Multi-Tenancy
- Complete data isolation between companies
- Row-level security enforced at database layer
- Tenant-specific file storage

### ✅ Asynchronous Processing
- Background workers process documents
- Non-blocking API responses
- Job queue management with Redis

### ✅ Security
- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (Admin, User, Viewer)
- Input validation and rate limiting

### ✅ Production-Ready
- Docker containerization
- Database migrations (Alembic)
- Comprehensive unit tests
- Structured JSON logging
- Error handling middleware

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────┐
│                  API Layer (FastAPI)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   Auth   │  │Document  │  │Middleware│            │
│  │   API    │  │   API    │  │          │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Service    │  │   Service    │  │   Service    │
│    Layer     │  │    Layer     │  │    Layer     │
│              │  │              │  │              │
│ Auth Service │  │ Document     │  │ Tenant       │
│              │  │ Service      │  │ Service      │
└──────────────┘  └──────────────┘  └──────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Data Access    │
                │     Layer       │
                │  (SQLAlchemy)   │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │ File Storage │
│   Database   │  │   (Queue)    │  │              │
└──────────────┘  └──────┬───────┘  └──────────────┘
                         │
                         │ Job Queue
                         │
                         ▼
                ┌──────────────┐
                │   Worker     │
                │   Process    │
                │ (Background) │
                └──────────────┘
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | High-performance async API framework |
| **Database** | PostgreSQL | Relational database with JSON support |
| **ORM** | SQLAlchemy | Database abstraction and migrations |
| **Queue** | Redis + RQ | Background job processing |
| **Auth** | JWT | Stateless authentication |
| **Validation** | Pydantic | Request/response validation |
| **Testing** | pytest | Unit and integration tests |
| **Containerization** | Docker | Development and deployment |

## 📦 Getting Started

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Multi Tenant Deocument Processing Platform"
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   make up
   # Or: docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   make migrate
   ```

5. **Seed sample data**
   ```bash
   make seed
   ```

6. **Access the API**
   - **API Base**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

### Quick Test

```bash
# 1. Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "password123",
    "full_name": "Demo User",
    "tenant_name": "Demo Company"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "password123"}'

# 3. Upload a document (use token from step 2)
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/document.pdf"
```

## 📚 API Documentation

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Documents

- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/` - List documents (with pagination)
- `GET /api/v1/documents/{id}` - Get document details

**Full API documentation available at**: http://localhost:8000/docs

## 📊 Accessing Extracted Data

### Via Web Interface

1. **Dashboard**: View summary statistics (total, pending, processing, completed documents)
2. **Documents Page**: 
   - See all documents with their status
   - View extracted metadata for completed documents
   - Filter by status (all, pending, processing, completed, failed)
   - Download original files
   - See extracted entities (dates, amounts, companies)

### Via API

#### Get All Documents
```bash
GET /api/v1/documents/
Authorization: Bearer <your_token>
```

#### Get Specific Document with Metadata
```bash
GET /api/v1/documents/{document_id}
Authorization: Bearer <your_token>
```

#### Download Original File
```bash
GET /api/v1/documents/{document_id}/download
Authorization: Bearer <your_token>
```

### What Data is Extracted?

- **Basic Metadata**: Page count, word count, language, document type
- **Entities**: Dates, amounts (currency), company names
- **Text Preview**: First 200 characters of extracted text
- **Full Text**: Complete extracted text (stored in database)

### Using the Data

The extracted metadata can be used for:
- **Search & Organization**: Find documents by content, type, or entities
- **Business Intelligence**: Track invoices, analyze trends
- **Automation**: Integrate with accounting systems, CRMs
- **Compliance**: Audit trails, reporting

See **[DATA_ACCESS_GUIDE.md](DATA_ACCESS_GUIDE.md)** for detailed information on accessing data, use cases, and improvement opportunities.

## 🧪 Testing

```bash
# Run all tests
make test

# Or manually
docker-compose exec api pytest -v --cov=app
```

## 📁 Project Structure

```
.
├── app/
│   ├── api/              # API routes
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── middleware/       # Logging, rate limiting
│   └── worker.py         # Background worker
├── alembic/              # Database migrations
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── docker-compose.yml    # Docker setup
└── requirements.txt     # Python dependencies
```

## 🌐 Making It Public

### Option 1: Deploy Backend to Free Hosting (Recommended)

#### Railway (Easiest)

1. **Sign up**: https://railway.app
2. **Create new project** → "Deploy from GitHub repo"
3. **Add services**:
   - PostgreSQL (database)
   - Redis (queue)
   - Your API (from Dockerfile)
4. **Set environment variables** from `.env.example`
5. **Deploy** → Get public URL

#### Render

1. **Sign up**: https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Settings**:
   - Build Command: `docker build -t app .`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add PostgreSQL and Redis** services
5. **Deploy**

#### Fly.io

1. **Install flyctl**: `curl -L https://fly.io/install.sh | sh`
2. **Login**: `fly auth login`
3. **Launch**: `fly launch` (in project directory)
4. **Add PostgreSQL**: `fly postgres create`
5. **Add Redis**: `fly redis create`
6. **Deploy**: `fly deploy`

### Option 2: Create a Frontend + Deploy Both

Create a simple React/Vue frontend that calls your deployed API:

1. **Deploy backend** (using Option 1 above)
2. **Create frontend** in a separate repo
3. **Deploy frontend** to:
   - **Vercel** (https://vercel.com) - Free, easy
   - **Netlify** (https://netlify.com) - Free, easy
   - **GitHub Pages** - Free, static only

### Option 3: GitHub Pages (Frontend Only)

Since GitHub Pages only hosts static sites, you can:

1. **Deploy backend** to Railway/Render/Fly.io
2. **Create simple HTML/JS frontend** that calls your API
3. **Host frontend** on GitHub Pages
4. **Update CORS** in backend to allow your GitHub Pages domain

## 📝 Sample Accounts

After running `make seed`, you can use:

- **Acme Corporation**: `admin@acme.com` / `admin123`
- **TechStart Inc**: `admin@techstart.com` / `admin123`
- **Global Industries**: `admin@global.com` / `admin123`

## 🎯 Why This Project Matters

This project demonstrates:

- ✅ **Real backend architecture** (not just algorithms)
- ✅ **Industry best practices** (auth, security, testing)
- ✅ **Production-ready code** (error handling, logging, migrations)
- ✅ **Understanding of scale** (multi-tenancy, async processing)
- ✅ **Modern tech stack** (FastAPI, PostgreSQL, Docker)

**Perfect for**: SWE internships, new grad positions, backend engineering roles

## 🤝 Contributing

This is a portfolio project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for educational and portfolio purposes.

## 👤 Author

Built as a demonstration of production-grade backend engineering practices.

---

**⭐ If you find this project helpful, please give it a star!**
