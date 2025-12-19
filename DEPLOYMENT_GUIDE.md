# 🚀 Deployment Guide

This guide will walk you through:
1. Pushing your code to GitHub
2. Deploying the frontend to Vercel
3. Deploying the backend to Railway

---

## 📋 Prerequisites

- GitHub account
- Vercel account (sign up at https://vercel.com - free)
- Railway account (sign up at https://railway.app - free $5/month credit)

---

## Part 1: Push to GitHub

### Step 1: Initialize Git (if not already done)

```bash
# Check if git is already initialized
git status

# If you see "fatal: not a git repository", initialize it:
git init
```

### Step 2: Review What Will Be Committed

```bash
# See all files that will be committed
git status

# .gitignore already excludes:
# - node_modules/
# - .env files
# - Python cache files
# - dist/ build folders
```

### Step 3: Commit Your Code

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Full-stack Flashfood Tracker

- FastAPI backend with JWT auth
- React + TypeScript frontend
- PostgreSQL database with 5 models
- WebSocket real-time notifications
- Background task scheduler
- Docker Compose setup
- Vercel and Railway deployment configs"

# Check commit was successful
git log
```

### Step 4: Create GitHub Repository

**Option A: Via GitHub Website**
1. Go to https://github.com/new
2. Repository name: `Flashfood-Tracker` (or keep current name)
3. Description: "Full-stack web app for tracking Flashfood grocery deals with real-time notifications"
4. Public (for portfolio visibility)
5. **DO NOT** initialize with README (you already have one)
6. Click "Create repository"

**Option B: Via GitHub CLI (if installed)**
```bash
gh repo create Flashfood-Tracker --public --source=. --remote=origin
```

### Step 5: Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Flashfood-Tracker.git

# If you already have a remote called origin:
git remote set-url origin https://github.com/YOUR_USERNAME/Flashfood-Tracker.git

# Push to GitHub
git push -u origin main

# If your branch is called "master" instead of "main":
git branch -M main
git push -u origin main
```

### Step 6: Verify Upload

1. Go to https://github.com/YOUR_USERNAME/Flashfood-Tracker
2. You should see all your files
3. README.md should display nicely

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Sign Up for Vercel

1. Go to https://vercel.com/signup
2. Click "Continue with GitHub"
3. Authorize Vercel to access your repositories

### Step 2: Import Project

1. From Vercel dashboard, click "Add New..." → "Project"
2. Find your `Flashfood-Tracker` repository
3. Click "Import"

### Step 3: Configure Build Settings

Vercel should auto-detect these, but verify:

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 4: Add Environment Variables

Click "Environment Variables" and add:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-backend-url.railway.app` (You'll update this after deploying backend) |
| `VITE_WS_URL` | `wss://your-backend-url.railway.app/ws` (Same as above, but with `wss://`) |

**For now, use placeholder values:**
- `VITE_API_URL` = `http://localhost:8000`
- `VITE_WS_URL` = `ws://localhost:8000/ws`

You'll update these after deploying the backend.

### Step 5: Deploy

1. Click "Deploy"
2. Wait 1-2 minutes for build to complete
3. Click "Visit" to see your deployed frontend

### Step 6: Get Your Vercel URL

Your frontend will be deployed at:
```
https://flashfood-tracker-YOUR_USERNAME.vercel.app
```

**Save this URL** - you'll need it for backend CORS configuration.

---

## Part 3: Deploy Backend to Railway

### Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway

### Step 2: Create New Project

1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select your `Flashfood-Tracker` repository
4. Railway will detect the Dockerfile

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway automatically creates the database and sets environment variables

### Step 4: Add Redis Cache

1. Click "New Service" again
2. Select "Database" → "Redis"
3. Railway automatically creates Redis instance

### Step 5: Configure Backend Service

1. Click on your backend service (the one running the Dockerfile)
2. Go to "Settings" tab
3. Set **Root Directory** to `backend`
4. Set **Start Command** to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 6: Add Environment Variables

Click "Variables" tab and add these:

| Variable | Value | Notes |
|----------|-------|-------|
| `SECRET_KEY` | Generate random 32+ character string | Use generator below |
| `POSTGRES_USER` | (Auto-filled by Railway) | Don't change |
| `POSTGRES_PASSWORD` | (Auto-filled by Railway) | Don't change |
| `POSTGRES_HOST` | (Auto-filled by Railway) | Don't change |
| `POSTGRES_PORT` | (Auto-filled by Railway) | Don't change |
| `POSTGRES_DB` | (Auto-filled by Railway) | Don't change |
| `REDIS_HOST` | (Auto-filled by Railway) | Don't change |
| `REDIS_PORT` | (Auto-filled by Railway) | Don't change |
| `BACKEND_CORS_ORIGINS` | `["https://your-vercel-url.vercel.app"]` | Use your Vercel URL from Part 2 |
| `RESEND_API_KEY` | (Optional) Get from https://resend.com | For email notifications |
| `EMAIL_FROM` | `notifications@yourdomain.com` | For email notifications |

**Generate SECRET_KEY:**

**On macOS/Linux:**
```bash
openssl rand -hex 32
```

**On Windows PowerShell:**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Or use online generator:**
https://randomkeygen.com/ (use "CodeIgniter Encryption Keys")

### Step 7: Deploy

1. Click "Deploy" (or Railway auto-deploys when you add variables)
2. Wait 2-3 minutes for deployment
3. Check "Deployments" tab for build logs

### Step 8: Get Your Railway URL

1. Go to "Settings" tab
2. Scroll to "Domains"
3. Click "Generate Domain"
4. You'll get: `https://your-app-name.up.railway.app`

**Save this URL** - this is your backend API.

### Step 9: Test Backend

Visit your Railway URL:
```
https://your-app-name.up.railway.app/health
```

You should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "project": "Flashfood Tracker"
}
```

Visit API docs:
```
https://your-app-name.up.railway.app/docs
```

You should see interactive API documentation!

---

## Part 4: Connect Frontend to Backend

### Step 1: Update Vercel Environment Variables

1. Go to your Vercel project
2. Click "Settings" → "Environment Variables"
3. Update these variables:

| Variable | New Value |
|----------|-----------|
| `VITE_API_URL` | `https://your-app-name.up.railway.app` |
| `VITE_WS_URL` | `wss://your-app-name.up.railway.app/ws` |

### Step 2: Redeploy Frontend

1. Go to "Deployments" tab
2. Click "..." on latest deployment
3. Click "Redeploy"
4. Or just push a new commit to GitHub (triggers auto-deploy)

### Step 3: Update Backend CORS

1. Go to Railway backend service
2. Update `BACKEND_CORS_ORIGINS` variable:
   ```json
   ["https://your-vercel-url.vercel.app"]
   ```
3. Railway will auto-redeploy

---

## Part 5: Test Everything

### Step 1: Visit Your Frontend

Go to: `https://your-vercel-url.vercel.app`

### Step 2: Create Account

1. Click "Sign up"
2. Enter email and password
3. Click "Create account"

### Step 3: Verify It Works

You should:
1. Be redirected to dashboard
2. See loading spinner
3. See message: "No deals found" (normal - database is empty)

### Step 4: Trigger Initial Data Population

The background scheduler will run every 5 minutes and populate the database automatically. To speed this up:

**Option 1: Wait 5 minutes** (scheduler runs automatically)

**Option 2: Manually trigger** (requires backend access)
```bash
# SSH into Railway container (from Railway dashboard)
# Then run:
python -c "import asyncio; from app.services.scheduler import FlashfoodScheduler; s = FlashfoodScheduler(); asyncio.run(s.fetch_and_update_deals())"
```

### Step 5: Check for Deals

Refresh the dashboard after 5 minutes. You should see deals appearing!

---

## Part 6: Set Up Custom Domain (Optional)

### For Frontend (Vercel)

1. Buy a domain (Namecheap, Google Domains, etc.)
2. In Vercel, go to "Settings" → "Domains"
3. Add your domain: `flashfoodtracker.com`
4. Follow Vercel's DNS instructions
5. Update backend CORS to include your custom domain

### For Backend (Railway)

1. In Railway, go to "Settings" → "Domains"
2. Click "Custom Domain"
3. Add: `api.flashfoodtracker.com`
4. Update DNS with CNAME record
5. Update frontend environment variables to use custom domain

---

## 🔧 Troubleshooting

### Frontend shows "Network Error"

**Cause:** Backend URL is wrong or CORS not configured

**Fix:**
1. Check `VITE_API_URL` in Vercel matches your Railway URL
2. Check `BACKEND_CORS_ORIGINS` in Railway includes your Vercel URL
3. Ensure both start with `https://` (not `http://`)

### "Could not validate credentials" error

**Cause:** JWT token issue or database connection problem

**Fix:**
1. Check `SECRET_KEY` is set in Railway
2. Try logging out and logging back in
3. Check Railway logs for errors: `railway logs`

### No deals showing up

**Cause:** Database is empty or scheduler hasn't run yet

**Fix:**
1. Wait 5 minutes for scheduler to run
2. Check Railway logs to see if scheduler is working
3. Look for "Starting Flashfood deal refresh cycle..." in logs

### Build failed on Vercel

**Cause:** TypeScript errors or missing dependencies

**Fix:**
1. Check build logs in Vercel
2. Run `npm run build` locally in `frontend/` directory
3. Fix any TypeScript errors
4. Push fixes to GitHub

### Build failed on Railway

**Cause:** Python errors or missing environment variables

**Fix:**
1. Check deployment logs in Railway
2. Ensure all required environment variables are set
3. Check for Python syntax errors

---

## 📊 Monitoring Your Deployment

### Check Backend Health

Visit: `https://your-railway-url.railway.app/health`

Should return:
```json
{"status": "healthy", "version": "1.0.0"}
```

### View Backend Logs

In Railway:
1. Click on backend service
2. Go to "Deployments" tab
3. Click on latest deployment
4. View real-time logs

### View Frontend Logs

In Vercel:
1. Go to "Deployments"
2. Click on latest deployment
3. Click "View Function Logs" (if using serverless functions)

### Check Database

In Railway:
1. Click on PostgreSQL service
2. Click "Data" tab
3. Run SQL queries to see data:
   ```sql
   SELECT COUNT(*) FROM "user";
   SELECT COUNT(*) FROM store;
   SELECT COUNT(*) FROM product;
   ```

---

## 🎯 Next Steps

1. **Add GitHub Actions CI/CD** (automatically test on push)
2. **Set up monitoring** (Sentry for error tracking)
3. **Add analytics** (Google Analytics or Plausible)
4. **Custom domain** (looks more professional)
5. **Share with family** (get real user feedback!)

---

## 📝 Environment Variables Cheat Sheet

### Backend (Railway)

```bash
# Required
SECRET_KEY=<random-32-char-string>
POSTGRES_USER=<auto-filled>
POSTGRES_PASSWORD=<auto-filled>
POSTGRES_HOST=<auto-filled>
POSTGRES_PORT=<auto-filled>
POSTGRES_DB=<auto-filled>
REDIS_HOST=<auto-filled>
REDIS_PORT=<auto-filled>
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]

# Optional
RESEND_API_KEY=re_xxxxx
EMAIL_FROM=notifications@yourdomain.com
```

### Frontend (Vercel)

```bash
VITE_API_URL=https://your-backend.railway.app
VITE_WS_URL=wss://your-backend.railway.app/ws
```

---

## 🎉 You're Done!

Your app is now live at:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app
- **API Docs**: https://your-app.railway.app/docs

Share the frontend URL with your family and add it to your resume! 🚀
