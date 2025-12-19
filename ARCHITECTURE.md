# 🏗️ Architecture & Technology Guide

This document explains **every piece** of the Flashfood Tracker architecture, what each technology does, and **why** we chose it.

---

## 📊 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER'S BROWSER                                │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    React Frontend (Port 5173)                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │  Login   │  │ Register │  │Dashboard │  │ Settings │        │   │
│  │  │  Page    │  │   Page   │  │   Page   │  │   Page   │        │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │   │
│  │                                                                   │   │
│  │  React Router (Navigation) + TanStack Query (Data Fetching)     │   │
│  │  Tailwind CSS (Styling) + TypeScript (Type Safety)              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                         │
│                                 │ HTTP Requests (REST API)               │
│                                 │ WebSocket Connection (Real-time)       │
└─────────────────────────────────┼─────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Port 8000)                          │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      API Routes (Endpoints)                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │  /auth   │  │ /stores  │  │/products │  │  /prefs  │        │   │
│  │  │ register │  │   list   │  │  search  │  │  update  │        │   │
│  │  │  login   │  │  detail  │  │  filter  │  │   get    │        │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Business Logic Layer                          │   │
│  │                                                                   │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │   │
│  │  │ Flashfood API  │  │ Email Service  │  │  WebSocket     │    │   │
│  │  │   Service      │  │   (Resend)     │  │  Manager       │    │   │
│  │  │ - Fetch stores │  │ - Send alerts  │  │ - Broadcast    │    │   │
│  │  │ - Get items    │  │ - Price drops  │  │ - Real-time    │    │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘    │   │
│  │                                                                   │   │
│  │  ┌────────────────────────────────────────────────────────┐     │   │
│  │  │         Background Scheduler (APScheduler)             │     │   │
│  │  │  - Runs every 5 minutes                                │     │   │
│  │  │  - Polls Flashfood API for all cities                  │     │   │
│  │  │  - Detects new deals                                   │     │   │
│  │  │  - Broadcasts WebSocket notifications                  │     │   │
│  │  │  - Sends email alerts to subscribed users              │     │   │
│  │  └────────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Access Layer (ORM)                       │   │
│  │                      SQLAlchemy Models                           │   │
│  │  ┌──────┐  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ User │  │Store │  │ Product │  │  Price   │  │   User   │  │   │
│  │  │      │  │      │  │         │  │ History  │  │Preference│  │   │
│  │  └──────┘  └──────┘  └─────────┘  └──────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬───────────────────┬─────────────────────┘
                                │                   │
                    ┌───────────▼─────┐   ┌────────▼────────┐
                    │  PostgreSQL DB  │   │  Redis Cache    │
                    │   (Port 5432)   │   │  (Port 6379)    │
                    │                 │   │                 │
                    │ - Users         │   │ - API responses │
                    │ - Stores        │   │ - Session data  │
                    │ - Products      │   │ - Fast lookups  │
                    │ - Price history │   │                 │
                    └─────────────────┘   └─────────────────┘
```

---

## 🔧 Technology Stack Explained

### **Frontend Technologies**

#### 1. **React 18** - UI Library
**What it is:** A JavaScript library for building user interfaces using components.

**Why we use it:**
- **Component-based**: Break UI into reusable pieces (DealCard, Navbar, etc.)
- **Virtual DOM**: Fast updates without refreshing the entire page
- **Hooks**: Modern way to manage state and side effects
- **Industry standard**: Most companies use React

**Example in our project:**
```typescript
// LoginPage.tsx - A React component
export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');  // State management
  return <form>...</form>;  // JSX (HTML-like syntax)
}
```

**Analogy:** Think of React like building with LEGO blocks. Each component (Login button, Deal card, Navbar) is a reusable block you can combine.

---

#### 2. **TypeScript** - Type-Safe JavaScript
**What it is:** JavaScript with type checking to catch errors before runtime.

**Why we use it:**
- **Catch bugs early**: TypeScript errors show in your editor before you run code
- **Better autocomplete**: Your editor knows what properties objects have
- **Self-documenting**: Types explain what data looks like
- **Required for large projects**: Prevents "undefined is not a function" errors

**Example:**
```typescript
// Without TypeScript (JavaScript)
function login(data) {
  return fetch('/api/login', { body: data });  // What is data? Who knows!
}

// With TypeScript
interface LoginRequest {
  username: string;
  password: string;
}

function login(data: LoginRequest) {
  return fetch('/api/login', { body: data });  // TypeScript ensures data is correct!
}
```

**Analogy:** TypeScript is like having a strict teacher who checks your homework before you turn it in.

---

#### 3. **Vite** - Build Tool
**What it is:** A fast development server and build tool for modern web apps.

**Why we use it:**
- **Blazing fast**: Hot Module Replacement (HMR) updates instantly
- **Modern**: Works with ES modules natively
- **Simple config**: Less boilerplate than Webpack
- **Optimized builds**: Produces small, fast production bundles

**What it does:**
1. Development: Runs a server at `localhost:5173`
2. Hot reload: Changes appear instantly without refresh
3. Build: Bundles your app into optimized static files

**Analogy:** Vite is like a chef who preps ingredients (compiles code) instantly and serves hot food (hot reload) immediately.

---

#### 4. **TailwindCSS** - Utility-First CSS Framework
**What it is:** A CSS framework that provides utility classes for styling.

**Why we use it:**
- **Fast styling**: No need to write custom CSS files
- **Consistent design**: Pre-defined spacing, colors, fonts
- **Responsive**: Built-in mobile-first responsive classes
- **Small bundle**: Only includes classes you actually use

**Example:**
```tsx
// Traditional CSS
<div className="login-button">Login</div>
// Requires separate CSS file:
.login-button { background-color: green; padding: 12px; border-radius: 6px; }

// Tailwind CSS
<button className="bg-green-500 px-4 py-3 rounded-lg">Login</button>
// All styling inline! No CSS file needed.
```

**Analogy:** Tailwind is like having pre-cut fabric patches instead of sewing from scratch.

---

#### 5. **React Router** - Client-Side Routing
**What it is:** Handles navigation between pages without full page reloads.

**Why we use it:**
- **SPA navigation**: Change URLs without server requests
- **Protected routes**: Require login for certain pages
- **URL parameters**: `/products/:id` extracts product ID from URL

**Example:**
```tsx
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/dashboard" element={<DashboardPage />} />
</Routes>
```

**Analogy:** React Router is like a GPS that changes the "location" in your browser without actually navigating to a new website.

---

#### 6. **TanStack Query (React Query)** - Data Fetching
**What it is:** A library for fetching, caching, and updating server data.

**Why we use it:**
- **Automatic caching**: Fetched data is cached, reducing API calls
- **Auto-refetching**: Refreshes stale data in the background
- **Loading/error states**: Handles loading spinners and errors automatically
- **Optimistic updates**: Update UI before server responds

**Example:**
```tsx
const { data: products, isLoading } = useQuery({
  queryKey: ['products', city],
  queryFn: () => productApi.listProducts({ city }),
});

// React Query handles:
// - Fetching data
// - Caching it
// - Re-fetching when 'city' changes
// - Loading state
// - Error handling
```

**Analogy:** React Query is like a smart librarian who remembers which books you asked for, updates them if they're outdated, and tells you when new ones arrive.

---

#### 7. **Axios** - HTTP Client
**What it is:** A promise-based HTTP client for making API requests.

**Why we use it:**
- **Interceptors**: Automatically add auth tokens to requests
- **Better errors**: More detailed error information than fetch
- **Request/response transforms**: Automatically parse JSON
- **Browser & Node support**: Works everywhere

**Example:**
```typescript
// Axios automatically adds JWT token to every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

**Analogy:** Axios is like a mail carrier who automatically stamps and addresses all your letters (adds auth headers).

---

### **Backend Technologies**

#### 8. **FastAPI** - Modern Python Web Framework
**What it is:** A modern, fast web framework for building APIs with Python.

**Why we use it:**
- **Automatic API docs**: Generates interactive docs at `/docs`
- **Type checking**: Uses Python type hints for validation
- **Async support**: Handle multiple requests simultaneously
- **Fast**: One of the fastest Python frameworks (comparable to Node.js)
- **Modern**: Better than Flask/Django for APIs

**Example:**
```python
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # FastAPI automatically:
    # - Validates form_data structure
    # - Parses request body
    # - Generates OpenAPI docs
    # - Handles errors
    return {"access_token": token}
```

**Analogy:** FastAPI is like a restaurant waiter who takes orders, validates them, sends them to the kitchen, and brings back food—all automatically.

---

#### 9. **SQLAlchemy** - Database ORM
**What it is:** Object-Relational Mapper that lets you work with databases using Python objects.

**Why we use it:**
- **No SQL writing**: Use Python instead of SQL queries
- **Type-safe**: Catch errors before hitting database
- **Relationship management**: Handles foreign keys automatically
- **Database agnostic**: Works with PostgreSQL, MySQL, SQLite, etc.

**Example:**
```python
# Without ORM (raw SQL)
cursor.execute("SELECT * FROM user WHERE email = ?", [email])
user = cursor.fetchone()

# With SQLAlchemy ORM
user = db.query(User).filter(User.email == email).first()
# Much cleaner! And type-safe.
```

**Analogy:** SQLAlchemy is like speaking to a database in Python instead of its native language (SQL).

---

#### 10. **PostgreSQL** - Relational Database
**What it is:** A powerful, open-source relational database.

**Why we use it:**
- **Relational**: Perfect for data with relationships (users → preferences, stores → products)
- **ACID compliant**: Guarantees data integrity
- **Rich features**: JSON support, full-text search, geospatial queries
- **Production-ready**: Used by major companies (Instagram, Spotify)

**How data is organized:**
```sql
User (id, email, password)
  ↓ (one-to-one)
UserPreference (id, user_id, city, email_notifications)

Store (id, name, city, latitude, longitude)
  ↓ (one-to-many)
Product (id, store_id, name, price, discount_price)
  ↓ (one-to-many)
PriceHistory (id, product_id, price, recorded_at)
```

**Analogy:** PostgreSQL is like an organized filing cabinet with drawers (tables) and folders (rows) that have strict labels (columns).

---

#### 11. **Redis** - In-Memory Cache
**What it is:** A super-fast in-memory key-value store used for caching.

**Why we use it:**
- **Extremely fast**: Data stored in RAM, not disk
- **Reduces API calls**: Cache Flashfood API responses for 5 minutes
- **Prevents rate limiting**: Don't hit Flashfood API too frequently
- **Session storage**: Could store user sessions here

**Example:**
```python
# First request - hits Flashfood API (slow)
response = flashfood_api.get_stores()
redis.set("stores:calgary", response, ex=300)  # Cache for 5 minutes

# Second request - hits Redis (fast!)
cached = redis.get("stores:calgary")  # Returns instantly
```

**Analogy:** Redis is like sticky notes on your desk for quick lookups, instead of walking to the filing cabinet every time.

---

#### 12. **Pydantic** - Data Validation
**What it is:** Python library for data validation using type annotations.

**Why we use it:**
- **Request validation**: Ensure API requests have correct data
- **Automatic docs**: FastAPI uses Pydantic to generate API docs
- **Type safety**: Catch errors before they reach your code
- **Serialization**: Convert Python objects to JSON automatically

**Example:**
```python
class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=8)

# If someone sends {"username": "test@example.com", "password": "123"}
# Pydantic raises an error: "password must be at least 8 characters"
```

**Analogy:** Pydantic is like a bouncer at a club checking IDs—only valid data gets in.

---

#### 13. **APScheduler** - Background Task Scheduler
**What it is:** A Python library for scheduling tasks to run at intervals.

**Why we use it:**
- **Periodic tasks**: Run code every X minutes/hours
- **Non-blocking**: Doesn't stop the API from serving requests
- **Reliable**: Handles failures and retries

**How we use it:**
```python
scheduler.add_job(
    fetch_flashfood_deals,  # Function to run
    "interval",
    seconds=300,  # Every 5 minutes
)
```

**Our scheduled task:**
1. Fetch deals from Flashfood API for all cities
2. Compare with database to find new deals
3. Save new deals to database
4. Broadcast WebSocket notification
5. Send email alerts to users

**Analogy:** APScheduler is like setting recurring alarms on your phone.

---

#### 14. **WebSockets** - Real-Time Communication
**What it is:** A protocol for two-way communication between client and server.

**Why we use it:**
- **Real-time updates**: Server can push data to client instantly
- **Persistent connection**: No need to poll the server repeatedly
- **Low latency**: Messages arrive in milliseconds

**How it works:**
```
Client connects → Server accepts → Connection stays open
↓
Background task detects new deal
↓
Server broadcasts message to all connected clients
↓
Clients receive notification instantly
```

**Analogy:** WebSocket is like a phone call (two-way, real-time) vs. traditional HTTP which is like texting (one-way, request-response).

---

#### 15. **JWT (JSON Web Tokens)** - Authentication
**What it is:** A secure way to transmit user identity between client and server.

**Why we use it:**
- **Stateless**: Server doesn't need to store session data
- **Secure**: Signed with a secret key, can't be tampered with
- **Portable**: Works across multiple servers/services
- **Standard**: Industry-standard authentication method

**How it works:**
```
1. User logs in → Server creates JWT → Returns to client
2. Client stores JWT in localStorage
3. Every request includes JWT in Authorization header
4. Server verifies JWT signature and extracts user ID
```

**JWT structure:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  ← Header
eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIn0.    ← Payload (user email)
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← Signature
```

**Analogy:** JWT is like an ID badge with a holographic sticker that proves it's authentic.

---

### **Infrastructure & DevOps**

#### 16. **Docker** - Containerization
**What it is:** Packages your application with all dependencies into a container.

**Why we use it:**
- **Consistency**: "Works on my machine" → "Works everywhere"
- **Isolation**: Each service (database, backend, frontend) runs independently
- **Easy setup**: One command (`docker-compose up`) starts everything
- **Production-ready**: Same container runs locally and in production

**What's a container?**
Think of it as a lightweight virtual machine. It includes:
- Your code
- Python/Node.js runtime
- All libraries and dependencies
- Operating system libraries

**Example:**
```dockerfile
# Dockerfile defines what goes in the container
FROM python:3.11-slim        # Start with Python installed
COPY requirements.txt .      # Copy dependency list
RUN pip install -r requirements.txt  # Install dependencies
COPY ./app ./app             # Copy your code
CMD ["uvicorn", "app.main:app"]  # Run the app
```

**Analogy:** Docker is like shipping your app in a complete, self-contained box with everything it needs to run.

---

#### 17. **Docker Compose** - Multi-Container Orchestration
**What it is:** Tool for defining and running multi-container Docker applications.

**Why we use it:**
- **Multiple services**: Start database, cache, backend, frontend with one command
- **Networking**: Containers can talk to each other by name
- **Environment variables**: Configure services without changing code
- **Development parity**: Same setup on all developers' machines

**Our docker-compose.yml:**
```yaml
services:
  postgres:    # Database service
  redis:       # Cache service
  backend:     # FastAPI app
  frontend:    # React app (not included in current setup)
```

**One command starts all 3:**
```bash
docker-compose up
```

**Analogy:** Docker Compose is like a conductor leading an orchestra—coordinates multiple services to work together.

---

#### 18. **Vercel** - Frontend Hosting
**What it is:** Platform for deploying frontend applications (React, Next.js, etc.).

**Why we use it:**
- **Free tier**: Perfect for portfolio projects
- **Automatic deployments**: Push to GitHub → Vercel deploys
- **CDN**: Your app loads fast worldwide
- **Preview deployments**: Each PR gets a test URL

**How it works:**
1. Connect GitHub repo to Vercel
2. Push code → Vercel automatically builds and deploys
3. Get a URL: `flashfood-tracker.vercel.app`

**Analogy:** Vercel is like an auto-publish button for your website.

---

#### 19. **Railway** - Backend Hosting
**What it is:** Platform for deploying backend applications and databases.

**Why we use it:**
- **Free tier**: $5/month free credit
- **Automatic deployments**: Push to GitHub → Railway deploys
- **Built-in database**: PostgreSQL + Redis included
- **Environment variables**: Secure config management
- **Docker support**: Automatically detects Dockerfile

**What Railway provides:**
- Backend server running FastAPI
- PostgreSQL database
- Redis cache
- All connected and configured

**Analogy:** Railway is like renting a pre-configured server that auto-updates when you push code.

---

## 🧩 Why This Architecture?

### **Separation of Concerns**
Each layer has one job:
- **Frontend**: Display data, handle user input
- **Backend API**: Process requests, enforce business logic
- **Database**: Store data reliably
- **Cache**: Speed up repeated requests

### **Scalability**
- **Stateless backend**: Can run multiple backend instances
- **Database**: Can add read replicas for more traffic
- **Cache**: Reduces database load by 80%+
- **CDN (Vercel)**: Frontend loads fast worldwide

### **Maintainability**
- **TypeScript**: Catch bugs early
- **Modular code**: Each file has one purpose
- **ORM**: Change databases without rewriting queries
- **Docker**: Same environment everywhere

### **Security**
- **JWT**: Secure authentication
- **Bcrypt**: Password hashing (irreversible)
- **Pydantic**: Input validation (prevents injection)
- **CORS**: Only allow requests from frontend domain
- **Environment variables**: Secrets not in code

---

## 📁 Project Structure Explained

```
backend/app/
├── api/v1/endpoints/     ← API route handlers (controllers)
│   ├── auth.py           ← Login, register, get current user
│   ├── stores.py         ← List stores, get store details
│   ├── products.py       ← Search products, filter, get history
│   └── preferences.py    ← User notification settings
│
├── models/               ← Database table definitions (ORM)
│   ├── user.py           ← User table
│   ├── store.py          ← Store table
│   ├── product.py        ← Product table
│   ├── price_history.py  ← Price history table
│   └── user_preference.py ← User settings table
│
├── schemas/              ← Request/response validation
│   ├── user.py           ← UserCreate, UserResponse, Token
│   ├── store.py          ← StoreResponse, StoreWithDistance
│   ├── product.py        ← ProductResponse, ProductWithHistory
│   └── preference.py     ← UserPreferenceUpdate
│
├── services/             ← Business logic (NOT tied to HTTP)
│   ├── flashfood.py      ← Flashfood API integration
│   ├── scheduler.py      ← Background polling task
│   ├── email.py          ← Email notification service
│   └── websocket.py      ← WebSocket connection manager
│
├── core/                 ← App-wide utilities
│   ├── config.py         ← Settings from environment variables
│   └── security.py       ← JWT creation, password hashing
│
├── db/                   ← Database setup
│   ├── database.py       ← SQLAlchemy engine, session factory
│   └── base.py           ← Import all models (for Alembic)
│
└── main.py               ← FastAPI app entry point
```

**Why this structure?**
- **Easy to find code**: Want to change login? Go to `api/v1/endpoints/auth.py`
- **Testable**: Services are independent, easy to unit test
- **Reusable**: `flashfood.py` service can be used by API and scheduler
- **Scalable**: Add new endpoints without touching existing code

---

## 🔄 Request Flow Example

**User searches for deals in Calgary:**

```
1. User types "chicken" in search box
   ↓
2. React component calls: productApi.listProducts({ city: "calgary", search: "chicken" })
   ↓
3. Axios sends: GET /api/v1/products/?city=calgary&search=chicken
   ↓
4. FastAPI receives request at products.py:list_products()
   ↓
5. Endpoint queries database:
   db.query(Product).join(Store).filter(Store.city == "calgary", Product.name.ilike("%chicken%"))
   ↓
6. PostgreSQL returns matching products
   ↓
7. FastAPI serializes to JSON using ProductWithStore schema
   ↓
8. Response sent back to frontend
   ↓
9. React Query caches the results
   ↓
10. React renders DealCard components with data
```

**Total time: ~50-100ms**

---

## 🔄 Background Task Flow

**Scheduler detects new deal:**

```
Every 5 minutes:
1. APScheduler triggers fetch_and_update_deals()
   ↓
2. For each city (Calgary, Vancouver, etc.):
   ↓
3. FlashfoodService.get_stores_near_location(lat, lon)
   ↓
4. Check Redis cache first
   - Hit: Return cached data (fast!)
   - Miss: Fetch from Flashfood API, cache for 5 min
   ↓
5. For each store, fetch items
   ↓
6. Compare with database to detect new products
   ↓
7. If new deal found:
   a. Save to database
   b. Create price history entry
   c. Broadcast WebSocket message to all connected clients
   d. Send email to users with email_notifications=True
   ↓
8. Sleep until next interval
```

---

## 🎓 Key Concepts for Learning

### **Frontend Concepts**

1. **Component Lifecycle**: Mount → Update → Unmount
2. **State Management**: useState, useContext
3. **Side Effects**: useEffect for API calls
4. **Data Fetching**: React Query handles caching
5. **Routing**: Client-side navigation with React Router

### **Backend Concepts**

1. **REST API**: CRUD operations via HTTP methods (GET, POST, PATCH, DELETE)
2. **ORM**: Object-Relational Mapping (Python objects ↔ SQL tables)
3. **Authentication**: JWT tokens for stateless auth
4. **Validation**: Pydantic ensures data correctness
5. **Background Tasks**: Long-running tasks separate from API

### **Database Concepts**

1. **Normalization**: Separate tables to avoid data duplication
2. **Foreign Keys**: Link related data (Product → Store)
3. **Indexes**: Speed up queries (index on email for fast lookups)
4. **Transactions**: Ensure data consistency (all-or-nothing)

### **DevOps Concepts**

1. **Containerization**: Package app with dependencies
2. **Environment Variables**: Config without hardcoding
3. **CI/CD**: Automatic testing and deployment
4. **Caching**: Store frequently-accessed data in RAM

---

This architecture is **production-ready** and follows **industry best practices**. Every choice was made to balance simplicity (for learning) with real-world patterns (for your resume).
