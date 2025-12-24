# Deployment Guide

This guide explains how to make your document processing platform publicly accessible on the web.

## 🎯 Goal

Make your backend API accessible to anyone on the internet, so you can:
- Share it in your portfolio
- Demo it to recruiters
- Use it from a frontend application
- Show it off on your resume

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

**Why Railway?**
- Free tier with $5 credit/month
- Automatic deployments from GitHub
- Built-in PostgreSQL and Redis
- Simple setup

**Steps:**

1. **Sign up**: https://railway.app (use GitHub login)

2. **Create Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway automatically creates database

4. **Add Redis**:
   - Click "+ New" → "Database" → "Redis"
   - Railway automatically creates Redis instance

5. **Deploy API**:
   - Click "+ New" → "GitHub Repo" → Select your repo
   - Railway detects Dockerfile automatically
   - Set these environment variables:
     ```
     DATABASE_URL=<from PostgreSQL service>
     REDIS_URL=<from Redis service>
     JWT_SECRET_KEY=<generate a random string>
     ENVIRONMENT=production
     ```

6. **Run Migrations**:
   - In Railway dashboard, open your API service
   - Go to "Settings" → "Deploy"
   - Add build command: `alembic upgrade head`
   - Or run manually in "Shell" tab

7. **Get Public URL**:
   - Railway gives you a public URL like: `https://your-app.railway.app`
   - Your API is now live! 🎉

**Cost**: Free tier covers small projects

---

### Option 2: Render

**Why Render?**
- Free tier available
- Easy GitHub integration
- Good for small projects

**Steps:**

1. **Sign up**: https://render.com (use GitHub login)

2. **Create PostgreSQL Database**:
   - "New +" → "PostgreSQL"
   - Name it (e.g., "document-platform-db")
   - Copy the "Internal Database URL"

3. **Create Redis Instance**:
   - "New +" → "Redis"
   - Name it (e.g., "document-platform-redis")
   - Copy the "Internal Redis URL"

4. **Create Web Service**:
   - "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Name**: document-platform-api
     - **Environment**: Docker
     - **Dockerfile Path**: `Dockerfile`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL=<from PostgreSQL>
     REDIS_URL=<from Redis>
     JWT_SECRET_KEY=<random string>
     PORT=10000
     ENVIRONMENT=production
     ```

5. **Deploy**:
   - Click "Create Web Service"
   - Render builds and deploys automatically
   - Get public URL: `https://your-app.onrender.com`

**Cost**: Free tier (spins down after inactivity, but free)

---

### Option 3: Fly.io

**Why Fly.io?**
- Generous free tier
- Global edge network
- Good performance

**Steps:**

1. **Install flyctl**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Initialize**:
   ```bash
   cd "Multi Tenant Deocument Processing Platform"
   fly launch
   ```
   - Choose app name
   - Select region
   - Don't deploy yet (we need database first)

4. **Create PostgreSQL**:
   ```bash
   fly postgres create --name document-platform-db
   ```
   - Note the connection string

5. **Create Redis**:
   ```bash
   fly redis create --name document-platform-redis
   ```
   - Note the connection string

6. **Attach to app**:
   ```bash
   fly postgres attach document-platform-db
   fly redis attach document-platform-redis
   ```

7. **Set secrets**:
   ```bash
   fly secrets set JWT_SECRET_KEY="your-random-secret"
   fly secrets set ENVIRONMENT=production
   ```

8. **Deploy**:
   ```bash
   fly deploy
   ```

9. **Get URL**:
   ```bash
   fly status
   ```
   - Your app is at: `https://your-app.fly.dev`

**Cost**: Free tier covers small apps

---

## 🎨 Adding a Frontend (Optional)

To make it more user-friendly, add a simple frontend:

### Option A: Simple HTML/JS Frontend

1. **Create `frontend/` directory** in your repo
2. **Create `index.html`**:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Document Processing Platform</title>
   </head>
   <body>
       <h1>Document Processing Platform</h1>
       <div id="app">
           <input type="file" id="fileInput">
           <button onclick="uploadFile()">Upload</button>
           <div id="results"></div>
       </div>
       <script>
           const API_URL = 'https://your-deployed-api.railway.app';
           
           async function uploadFile() {
               const file = document.getElementById('fileInput').files[0];
               const formData = new FormData();
               formData.append('file', file);
               
               // First login (or use stored token)
               const loginRes = await fetch(`${API_URL}/api/v1/auth/login`, {
                   method: 'POST',
                   headers: {'Content-Type': 'application/json'},
                   body: JSON.stringify({
                       email: 'demo@example.com',
                       password: 'password123'
                   })
               });
               const {access_token} = await loginRes.json();
               
               // Upload file
               const res = await fetch(`${API_URL}/api/v1/documents/upload`, {
                   method: 'POST',
                   headers: {'Authorization': `Bearer ${access_token}`},
                   body: formData
               });
               const data = await res.json();
               document.getElementById('results').innerHTML = 
                   `<pre>${JSON.stringify(data, null, 2)}</pre>`;
           }
       </script>
   </body>
   </html>
   ```

3. **Deploy frontend to**:
   - **Vercel**: `vercel deploy`
   - **Netlify**: Drag & drop `frontend/` folder
   - **GitHub Pages**: Push to `gh-pages` branch

### Option B: React/Vue Frontend

1. **Create React app**:
   ```bash
   npx create-react-app frontend
   cd frontend
   ```

2. **Build UI** that calls your API

3. **Deploy to Vercel/Netlify**:
   - Connect GitHub repo
   - Auto-deploys on push

---

## 🔧 Post-Deployment Steps

### 1. Update CORS Settings

In `app/main.py`, update CORS to allow your frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "https://your-username.github.io",
        "http://localhost:3000"  # For local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Run Migrations

After deployment, run migrations:

**Railway**:
- Open service → "Shell" tab
- Run: `alembic upgrade head`

**Render**:
- Add to "Start Command": `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Fly.io**:
- Run: `fly ssh console -a your-app`
- Then: `alembic upgrade head`

### 3. Seed Sample Data (Optional)

```bash
# In deployed environment shell
python scripts/seed_data.py
```

### 4. Test Your Deployment

```bash
# Health check
curl https://your-app.railway.app/health

# Test API
curl https://your-app.railway.app/docs
```

---

## 📝 Environment Variables

Make sure these are set in your hosting platform:

```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
JWT_SECRET_KEY=<generate-random-string>
ENVIRONMENT=production
PORT=8000  # Or $PORT if platform provides it
```

**Generate JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 Troubleshooting

### Database Connection Issues
- Check `DATABASE_URL` format
- Ensure database is accessible from your app
- Check firewall/network settings

### Redis Connection Issues
- Verify `REDIS_URL` is correct
- Check Redis is running
- Ensure network connectivity

### CORS Errors
- Update `allow_origins` in CORS middleware
- Include your frontend URL
- Check browser console for specific errors

### Migration Errors
- Run migrations manually in shell
- Check database permissions
- Verify Alembic is installed

---

## 🎉 You're Live!

Once deployed, you can:
- Share the URL in your portfolio
- Add it to your resume
- Demo it in interviews
- Use it as a backend for other projects

**Example Portfolio Entry**:
> "Built a multi-tenant document processing platform deployed on Railway. 
> Live demo: https://your-app.railway.app/docs"

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Railway** | $5 credit/month | Pay as you go | Easiest setup |
| **Render** | Free (spins down) | $7/month | Simple projects |
| **Fly.io** | 3 VMs free | Pay as you go | Performance |
| **Heroku** | No free tier | $7/month | Legacy option |

**Recommendation**: Start with Railway for easiest setup, or Render for completely free option.

