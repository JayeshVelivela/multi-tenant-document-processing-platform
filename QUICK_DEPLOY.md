# 🚀 Quick Deploy Guide

Your code is ready! Follow these steps:

## Step 1: Push to GitHub

### 1.1 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `document-processing-platform` (or any name you like)
3. Make it **Public** (for free hosting) or **Private**
4. **DON'T** initialize with README, .gitignore, or license
5. Click "Create repository"

### 1.2 Push Your Code

Copy the commands GitHub shows you, or run:

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/document-processing-platform.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend (Railway) - 5 minutes ⭐

1. **Sign up**: https://railway.app (use "Login with GitHub")
2. **New Project** → "Deploy from GitHub repo"
3. **Select your repository**
4. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "PostgreSQL"
5. **Add Redis**:
   - Click "+ New" → "Database" → "Redis"
6. **Configure API Service**:
   - Click on your API service
   - Go to "Variables" tab
   - Add these (Railway auto-provides some):
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     REDIS_URL=${{Redis.REDIS_URL}}
     JWT_SECRET_KEY=your-super-secret-key-change-this-12345
     JWT_ALGORITHM=HS256
     STORAGE_PATH=/app/storage
     RATE_LIMIT_PER_MINUTE=60
     ```
7. **Deploy**: Railway builds automatically!
8. **Get URL**: Click on API service → "Settings" → Copy the domain (e.g., `your-app.up.railway.app`)

## Step 3: Deploy Frontend (Vercel) - 3 minutes ⭐

1. **Sign up**: https://vercel.com (use "Continue with GitHub")
2. **Add New Project** → Import your GitHub repo
3. **Configure**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (click "Edit" and set to `frontend`)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
4. **Environment Variables**:
   - Add: `VITE_API_URL` = `https://your-app.up.railway.app` (your Railway URL)
5. **Deploy**: Click "Deploy"!

## Step 4: Update CORS (Important!)

After deploying frontend, update backend CORS:

1. Go to Railway dashboard → Your API service
2. Click "Variables"
3. Add: `FRONTEND_URL` = `https://your-frontend.vercel.app`
4. Or manually edit `app/main.py` and add your Vercel URL to `allow_origins`

## Step 5: Run Database Migrations

In Railway:
1. Go to your API service
2. Click "Deployments" → Latest deployment
3. Click "View Logs"
4. Or use Railway's CLI:
   ```bash
   railway run alembic upgrade head
   ```

## ✅ Done!

Your site is live at:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/docs`

## 🎯 Quick Commands Reference

```bash
# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main

# Check if pushed
git remote -v
git log --oneline
```

## 🆘 Troubleshooting

**Backend won't start?**
- Check Railway logs
- Verify all environment variables are set
- Make sure PostgreSQL and Redis are running

**Frontend can't connect?**
- Check `VITE_API_URL` is correct
- Verify backend is running (check Railway)
- Check CORS settings

**Database errors?**
- Run migrations: `railway run alembic upgrade head`
- Check DATABASE_URL is correct

---

**Need help?** Check `DEPLOY_TO_GITHUB.md` for detailed instructions!

