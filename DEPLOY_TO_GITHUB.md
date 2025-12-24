# Deploy Your Document Platform for Free

This guide will help you:
1. Push your code to GitHub
2. Deploy the website for free (so it's accessible online, not just the code)

## 📦 Step 1: Push to GitHub

### Initialize Git (if not already done)

```bash
cd "/Users/jay/Documents/Multi Tenant Deocument Processing Platform"

# Initialize git
git init

# Create .gitignore if it doesn't exist
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Storage
storage/
*.pdf
*.doc
*.docx

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore
EOF

# Add all files
git add .

# Commit
git commit -m "Initial commit: Multi-Tenant Document Processing Platform"

# Create repository on GitHub first, then:
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/document-processing-platform.git
git branch -M main
git push -u origin main
```

## 🚀 Step 2: Deploy for Free

### Option 1: Railway (Easiest - Recommended) ⭐

**Why Railway?**
- Free tier with $5 credit/month
- Easy deployment
- Automatic HTTPS
- PostgreSQL and Redis included

**Steps:**

1. **Sign up**: https://railway.app (use GitHub to sign in)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Services**:
   - **PostgreSQL**: Click "+ New" → "Database" → "PostgreSQL"
   - **Redis**: Click "+ New" → "Database" → "Redis"
   - **API Service**: Click "+ New" → "GitHub Repo" → Select your repo

4. **Configure API Service**:
   - **Build Command**: Leave empty (uses Dockerfile)
   - **Start Command**: Leave empty (uses Dockerfile CMD)
   - **Port**: Set to `8000`

5. **Set Environment Variables**:
   Click on your API service → "Variables" tab → Add:
   ```
   DATABASE_URL=postgresql://postgres:password@postgres:5432/postgres
   REDIS_URL=redis://default:password@redis:6379
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   STORAGE_PATH=/app/storage
   RATE_LIMIT_PER_MINUTE=60
   ```

6. **Deploy**: Railway will automatically build and deploy!

7. **Get Your URL**: Railway gives you a URL like `https://your-app.up.railway.app`

### Option 2: Render (Also Easy)

**Steps:**

1. **Sign up**: https://render.com (use GitHub)

2. **Create Web Service**:
   - "New" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Build Command**: `docker build -t app .`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Environment**: `Docker`

3. **Add PostgreSQL**:
   - "New" → "PostgreSQL"
   - Copy the connection string

4. **Add Redis**:
   - "New" → "Redis"
   - Copy the connection string

5. **Set Environment Variables** in your Web Service

6. **Deploy**: Render will build and deploy automatically

### Option 3: Fly.io (More Control)

**Steps:**

1. **Install flyctl**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create app**:
   ```bash
   fly launch
   ```

4. **Add PostgreSQL**:
   ```bash
   fly postgres create
   ```

5. **Add Redis**:
   ```bash
   fly redis create
   ```

6. **Deploy**:
   ```bash
   fly deploy
   ```

## 🌐 Step 3: Deploy Frontend

### Option A: Vercel (Easiest for Frontend) ⭐

1. **Sign up**: https://vercel.com (use GitHub)

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import your GitHub repo
   - Select the `frontend` folder

3. **Configure**:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Environment Variables**:
   - `VITE_API_URL`: Your backend URL (from Railway/Render)

5. **Deploy**: Vercel will deploy automatically!

### Option B: Netlify

1. **Sign up**: https://netlify.com

2. **Deploy**:
   - "Add new site" → "Import an existing project"
   - Connect GitHub repo
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

3. **Environment Variables**: Add `VITE_API_URL`

## 🔧 Step 4: Update Frontend API URL

After deploying backend, update your frontend:

1. **Create `.env.production`** in `frontend/`:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```

2. **Or set in Vercel/Netlify**: Add as environment variable

3. **Rebuild frontend**:
   ```bash
   cd frontend
   npm run build
   ```

## 📝 Step 5: Update CORS

Update `app/main.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend.vercel.app",  # Add your frontend URL
        "https://your-frontend.netlify.app",  # Or Netlify URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ✅ Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed (Railway/Render/Fly.io)
- [ ] Frontend deployed (Vercel/Netlify)
- [ ] Environment variables set
- [ ] CORS updated
- [ ] Database migrations run
- [ ] Test the live site!

## 🎯 Recommended Setup

**Backend**: Railway (easiest, includes databases)
**Frontend**: Vercel (fastest, best for React)

## 💡 Pro Tips

1. **Use Railway's free tier** - $5 credit/month is enough for small projects
2. **Vercel is free forever** for personal projects
3. **Set up GitHub Actions** for automatic deployments
4. **Use environment variables** for all secrets
5. **Enable HTTPS** (automatic with Railway/Vercel)

## 🆘 Troubleshooting

**Backend won't start?**
- Check environment variables
- Verify database connection strings
- Check logs in Railway/Render dashboard

**Frontend can't connect?**
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Make sure backend is deployed and running

**Database issues?**
- Run migrations: `alembic upgrade head`
- Check connection string format
- Verify database is accessible

---

**Your site will be live at:**
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-api.railway.app`
- API Docs: `https://your-api.railway.app/docs`

Good luck! 🚀

