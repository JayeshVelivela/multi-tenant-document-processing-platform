# Frontend for Document Processing Platform

Modern React frontend for the Multi Tenant Document Processing Platform.

## Features

- 🎨 Beautiful, modern UI
- 📱 Responsive design
- 🔐 Authentication (Login/Register)
- 📄 Document upload and management
- 📊 Dashboard with statistics
- 🔍 Document filtering and search
- ⚡ Fast and lightweight

## Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL** (optional):
   Create `.env` file:
   ```
   VITE_API_URL=http://localhost:8000
   ```
   For production, set this to your deployed backend URL.

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## Development

The frontend runs on `http://localhost:3000` by default.

It automatically proxies API requests to `http://localhost:8000` (your backend).

## Deployment

### Vercel (Recommended)

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Set environment variable: `VITE_API_URL=https://your-backend.railway.app`

### Netlify

1. Drag and drop the `dist` folder after building
2. Set environment variable: `VITE_API_URL=https://your-backend.railway.app`

### GitHub Pages

1. Build: `npm run build`
2. Push `dist` folder to `gh-pages` branch
3. Enable GitHub Pages in repo settings

