# Frontend Setup Guide

## Quick Start

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open browser**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## What You Get

### 🎨 Beautiful UI
- Modern, clean design
- Responsive (works on mobile, tablet, desktop)
- Smooth animations and transitions
- Professional color scheme

### 📱 Pages

1. **Login Page**
   - Email/password authentication
   - Link to registration

2. **Register Page**
   - Create new account
   - Auto-login after registration

3. **Dashboard**
   - Welcome message
   - Statistics cards (total, pending, processing, completed)
   - Quick navigation

4. **Documents Page**
   - Upload documents (drag & drop or click)
   - View all documents
   - Filter by status (all, pending, processing, completed, failed)
   - See extracted metadata
   - Pagination support

### ✨ Features

- **Real-time Updates**: Refresh to see latest document status
- **File Upload**: Easy document upload with progress
- **Status Badges**: Color-coded status indicators
- **Metadata Display**: Shows extracted data in organized format
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Works on all screen sizes

## Configuration

### Local Development

The frontend automatically connects to `http://localhost:8000` (your backend).

### Production

1. **Set environment variable**:
   Create `.env` file:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

2. **Update CORS in backend**:
   In `app/main.py`, add your frontend URL:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "https://your-frontend.vercel.app",  # Add this
   ],
   ```

## Building for Production

```bash
cd frontend
npm run build
```

This creates a `dist` folder with optimized production files.

## Deployment Options

### Option 1: Vercel (Easiest)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

3. **Set environment variable**:
   - Go to Vercel dashboard
   - Settings → Environment Variables
   - Add: `VITE_API_URL=https://your-backend.railway.app`

### Option 2: Netlify

1. **Build**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**:
   - Go to https://netlify.com
   - Drag and drop the `dist` folder
   - Or connect GitHub repo

3. **Set environment variable**:
   - Site settings → Environment variables
   - Add: `VITE_API_URL=https://your-backend.railway.app`

### Option 3: GitHub Pages

1. **Build**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**:
   ```bash
   # Install gh-pages
   npm install -g gh-pages
   
   # Deploy
   cd dist
   git init
   git add .
   git commit -m "Deploy frontend"
   git branch -M gh-pages
   git remote add origin <your-repo-url>
   git push -u origin gh-pages
   ```

3. **Enable GitHub Pages**:
   - Go to repo settings
   - Pages → Source: `gh-pages` branch

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check backend CORS settings in `app/main.py`
2. Make sure your frontend URL is in `allow_origins`
3. Restart backend after changes

### API Connection Issues

1. Check `VITE_API_URL` is set correctly
2. Verify backend is running
3. Check browser console for errors

### Build Errors

1. Make sure all dependencies are installed: `npm install`
2. Check Node.js version (requires 16+)
3. Clear cache: `rm -rf node_modules && npm install`

## Customization

### Colors

Edit `src/index.css`:
```css
:root {
  --primary: #6366f1;  /* Change this */
  --primary-dark: #4f46e5;
  /* ... */
}
```

### Logo/Branding

Replace the title in:
- `src/pages/Login.jsx`
- `src/pages/Dashboard.jsx`
- `src/pages/Documents.jsx`

## Next Steps

1. ✅ Start frontend: `npm run dev`
2. ✅ Test all features
3. ✅ Customize colors/branding
4. ✅ Deploy backend (Railway/Render)
5. ✅ Deploy frontend (Vercel/Netlify)
6. ✅ Update CORS settings
7. ✅ Share your live demo! 🎉

