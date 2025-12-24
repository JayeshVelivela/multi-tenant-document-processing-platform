# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Make (optional, for convenience commands)

## Setup Steps

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```
   (Edit `.env` if needed, but defaults work for local development)

2. **Start all services**:
   ```bash
   make up
   ```
   This will:
   - Build Docker images
   - Start PostgreSQL, Redis, API, and Worker containers
   - Wait for services to be ready

3. **Run database migrations**:
   ```bash
   make migrate
   ```

4. **Seed sample data**:
   ```bash
   make seed
   ```

5. **Access the API**:
   - API Base: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Test the API

### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "password123",
    "full_name": "Demo User",
    "tenant_name": "Demo Company"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 3. Upload a document
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/your/document.pdf"
```

### 4. List documents
```bash
curl -X GET "http://localhost:8000/api/v1/documents/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Get specific document
```bash
curl -X GET http://localhost:8000/api/v1/documents/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Using Pre-seeded Accounts

After running `make seed`, you can use:

- **Acme Corporation**: `admin@acme.com` / `admin123`
- **TechStart Inc**: `admin@techstart.com` / `admin123`
- **Global Industries**: `admin@global.com` / `admin123`

## View Logs

```bash
make logs
```

## Run Tests

```bash
make test
```

## Stop Services

```bash
make down
```

## Clean Everything

```bash
make clean
```

This removes all containers, volumes, and data.

## Troubleshooting

### Services won't start
- Check if ports 8000, 5432, 6379 are available
- Ensure Docker has enough resources allocated

### Database connection errors
- Wait a few seconds after `make up` for PostgreSQL to initialize
- Check logs: `docker-compose logs postgres`

### Worker not processing jobs
- Check worker logs: `docker-compose logs worker`
- Verify Redis is running: `docker-compose ps redis`

### Migration errors
- Ensure database is running: `docker-compose ps postgres`
- Try: `docker-compose exec api alembic upgrade head`

