# 🍽️ Flashfood Tracker

A full-stack web application that aggregates and tracks grocery deals from Flashfood, providing real-time notifications and price history analysis.

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)

## 📋 Overview

Flashfood Tracker is a full-stack application that reverse-engineers the Flashfood mobile app's REST API to help users discover and track grocery deals from local stores. Built as a portfolio project to demonstrate modern web development practices, it features real-time notifications, price history tracking, and smart filtering across multiple Canadian cities.

### Key Features

- ✅ **User Authentication** - Secure JWT-based auth with email/password
- 📍 **Multi-City Support** - Calgary, Vancouver, Toronto, Edmonton, Waterloo/Kitchener
- 🔔 **Real-Time Notifications** - WebSocket push notifications for new deals
- 📧 **Email Alerts** - Customizable email notifications via Resend
- 📊 **Price History Tracking** - Track price changes over time
- 🔍 **Advanced Filtering** - Filter by city, category, discount percentage, and search
- 🎨 **Modern UI** - Responsive design with Tailwind CSS
- 🐳 **Containerized** - Full Docker Compose setup for local development

## 🏗️ Architecture

### Tech Stack

**Frontend**
- React 18 with TypeScript
- Vite for blazing-fast builds
- TailwindCSS for styling
- TanStack Query (React Query) for data fetching
- React Router for navigation
- Axios for HTTP requests
- WebSocket for real-time updates

**Backend**
- FastAPI (Python) for REST API
- SQLAlchemy for ORM
- PostgreSQL for data persistence
- Redis for caching
- APScheduler for background tasks
- Resend for email notifications
- HTTPX for async HTTP requests

**Infrastructure**
- Docker & Docker Compose for local development
- Vercel for frontend deployment
- Railway for backend + database deployment

### Project Structure

```
flashfood-tracker/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── api/             # API client and endpoints
│   │   ├── components/      # React components
│   │   ├── contexts/        # React context providers
│   │   ├── hooks/           # Custom React hooks
│   │   ├── pages/           # Page components
│   │   ├── types/           # TypeScript type definitions
│   │   └── App.tsx          # Main app component
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Config and security
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic services
│   │   └── main.py          # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml        # Local development setup
├── railway.toml              # Railway deployment config
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended)
- OR:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/flashfood-tracker.git
   cd flashfood-tracker
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env and set SECRET_KEY and other values

   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Start the application**
   ```bash
   docker-compose up
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Without Docker)

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

1. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   ```bash
   createdb flashfood
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the backend**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```

3. **Run the frontend**
   ```bash
   npm run dev
   ```

</details>

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password
- `GET /api/v1/auth/me` - Get current user profile

### Store Endpoints

- `GET /api/v1/stores/` - List all stores with distance calculation
- `GET /api/v1/stores/{id}` - Get specific store details

### Product Endpoints

- `GET /api/v1/products/` - List products with filters
- `GET /api/v1/products/{id}` - Get product with price history
- `GET /api/v1/products/categories/list` - List all categories

### Preference Endpoints

- `GET /api/v1/preferences/` - Get user preferences
- `PATCH /api/v1/preferences/` - Update user preferences

### WebSocket Endpoint

- `WS /ws?token={jwt_token}` - Real-time deal notifications

Full interactive API documentation available at `/docs` when running the backend.

## 🎯 How It Works

### Flashfood API Integration

The application reverse-engineers the Flashfood mobile app's REST API:

1. **Store Discovery** - Fetches stores near specified coordinates
2. **Item Retrieval** - Gets available deals for each store
3. **Background Polling** - Checks for new deals every 5 minutes
4. **Change Detection** - Compares with previous state to detect new items
5. **Notification Dispatch** - Sends alerts via WebSocket and email

### Database Schema

The application uses PostgreSQL with the following main tables:

- **user** - User accounts and authentication
- **store** - Store locations with geographic coordinates
- **product** - Current deals available at stores
- **price_history** - Historical price tracking for trend analysis
- **user_preference** - User notification preferences and filters

## 🚢 Deployment

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables:
   - `VITE_API_URL`: Your backend URL
   - `VITE_WS_URL`: Your WebSocket URL

### Backend (Railway)

1. Connect your GitHub repository to Railway
2. Add PostgreSQL and Redis services
3. Set environment variables from `backend/.env.example`
4. Railway will automatically detect the Dockerfile

## 🔐 Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens for secure authentication
- CORS configured for frontend domain
- Environment variables for sensitive data
- SQL injection protection via SQLAlchemy
- Input validation with Pydantic

## 📈 Future Enhancements

- [ ] Push notifications for mobile browsers
- [ ] Advanced price drop alert algorithms
- [ ] Map view of stores using Mapbox
- [ ] Product favorites and watchlists
- [ ] Advanced analytics dashboard
- [ ] SMS notifications via Twilio
- [ ] Admin panel for monitoring
- [ ] GitHub Actions CI/CD pipeline

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 About This Project

Built as a portfolio project to demonstrate full-stack development skills for internship applications.

**Technical Highlights:**
- Reverse-engineered mobile API using network inspection
- Designed scalable PostgreSQL schema with proper relationships
- Implemented JWT authentication from scratch
- Built real-time features using WebSockets
- Integrated third-party email service (Resend)
- Containerized with Docker for consistent deployments
- Followed TypeScript best practices with strict typing
- Used React Query for optimal data fetching patterns
- Implemented background task scheduling for API polling

## ⚠️ Disclaimer

This project is for educational purposes only. The Flashfood API is not public, and this application reverse-engineers their mobile app for learning purposes. Use responsibly and respect Flashfood's terms of service.

---

⭐ **Star this repo if you found it interesting!**
