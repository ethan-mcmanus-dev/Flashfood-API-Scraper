# 🚀 Quick Setup Guide

This guide will get you up and running with Flashfood Tracker in under 5 minutes using Docker.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Git installed
- A text editor (VS Code recommended)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/yourusername/Flashfood-API-Scraper.git
cd Flashfood-API-Scraper
```

### 2. Configure Backend Environment

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Open backend/.env in your text editor and set:
# - SECRET_KEY to a random 32+ character string
# - POSTGRES_PASSWORD (can keep default for local dev)
```

**Generate a SECRET_KEY (run in terminal):**
```bash
# On macOS/Linux
openssl rand -hex 32

# On Windows (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### 3. Configure Frontend Environment

```bash
cp frontend/.env.example frontend/.env
```

The defaults in `frontend/.env.example` work for local development!

### 4. Start Everything with Docker

```bash
docker-compose up
```

This will:
- Download all required images
- Start PostgreSQL database
- Start Redis cache
- Start FastAPI backend
- Start React frontend

**First run takes 2-3 minutes. Subsequent runs are much faster!**

### 5. Access the Application

Once you see "Application startup complete" in the logs:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Create Your First Account

1. Go to http://localhost:5173
2. Click "Sign up"
3. Enter your email and password
4. You'll be automatically redirected to the dashboard!

## Testing the Application

### Create a Test User

1. Register with any email (e.g., `test@example.com`)
2. Set a password (min 8 characters)
3. You'll be logged in automatically

### Explore Features

- **Filter by city**: Select Calgary, Vancouver, etc.
- **Search**: Type product names like "bread", "chicken"
- **Adjust discounts**: Move the slider to filter by minimum discount percentage
- **Real-time updates**: Leave the dashboard open and watch for new deal notifications

## Troubleshooting

### Port Already in Use

If you see "port is already allocated":

```bash
# Stop docker-compose
docker-compose down

# Check what's using the port
# On macOS/Linux
lsof -i :8000
lsof -i :5173

# On Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### Database Connection Errors

```bash
# Reset the database
docker-compose down -v
docker-compose up
```

### Frontend Not Loading

```bash
# Rebuild frontend
cd frontend
npm install
npm run build
```

## Development Tips

### View Logs

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### Stop Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove everything (including database!)
docker-compose down -v
```

### Run Backend Tests

```bash
cd backend
python -m pytest
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U flashfood -d flashfood

# View users
SELECT * FROM "user";

# View stores
SELECT * FROM store;

# View products
SELECT * FROM product LIMIT 10;
```

## Next Steps

### For Development

1. Make changes to frontend code - Vite will hot reload automatically
2. Make changes to backend code - FastAPI will auto-reload
3. Test with the interactive API docs at http://localhost:8000/docs

### For Production Deployment

See the main [README.md](README.md) for:
- Deploying frontend to Vercel
- Deploying backend to Railway
- Setting up production environment variables

## Common Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# View running containers
docker-compose ps

# Clean everything and start fresh
docker-compose down -v && docker-compose up --build
```

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- View API documentation at http://localhost:8000/docs
- Check Docker logs: `docker-compose logs`

---

Happy tracking! 🍽️
