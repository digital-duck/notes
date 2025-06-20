# Standalone Alpine.js Frontend Setup

## 📁 Project Structure
```
frontend/                          # New frontend project
├── package.json                   # Node.js dependencies
├── server.js                      # Express server for frontend
├── index.html                     # Alpine.js app with cross-origin API calls
└── assets/                        # Optional: local CSS/JS files

backend/                           # Your existing FastAPI backend
├── main.py                        # FastAPI app (needs CORS updates)
├── static/                        # No longer needed for frontend
└── notes.db                       # SQLite database
```

## 🚀 Setup Steps

### Step 1: Create Frontend Project
```bash
# Create new directory for frontend
mkdir frontend
cd frontend

# Initialize Node.js project
npm init -y

# Install dependencies
npm install express cors
npm install --save-dev nodemon
```

### Step 2: Update FastAPI Backend for CORS
Update your `main.py` to properly handle cross-origin requests:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Note Taking API")

# CRITICAL: Enable CORS for standalone frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3100", "http://127.0.0.1:3100"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Remove or comment out static file mounting
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Remove frontend serving routes (/, /basic, etc.)
# @app.get("/")
# async def serve_frontend():
#     return FileResponse("static/index.html")

# Keep only your API routes
@app.get("/api/notes")
async def get_notes():
    # Your existing API code
    pass
```

### Step 3: Run Both Services

**Terminal 1 - Backend (FastAPI):**
```bash
cd backend
# python main.py

uvicorn main:app --reload --host 0.0.0.0 --port 8000
# FastAPI runs on http://localhost:8000
```

**Terminal 2 - Frontend (Node.js):**
```bash
cd frontend
PORT=3100 npm start

# if you want auto-restart with nodemon on the new
# PORT=3100 npm run dev 

# Express frontend runs on http://localhost:3100
```

### Step 4: Test the Setup
1. **Backend API**: http://localhost:8000/api/notes
2. **Frontend App**: http://localhost:3100
3. **Connection Test**: Click "Test API Connection" button

## 🔧 How Cross-Origin Communication Works

### 1. **Separate Domains**
- **Frontend**: `http://localhost:3100` (Node.js/Express)
- **Backend**: `http://localhost:8000` (FastAPI)

### 2. **CORS Headers**
FastAPI sends these headers to allow cross-origin requests:
```
Access-Control-Allow-Origin: http://localhost:3100
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
```

### 3. **Alpine.js API Calls**
```javascript
// The frontend makes requests to the backend domain
const response = await fetch('http://localhost:8000/api/notes', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    }
});
```

## 🎯 Key Learning Points

### **1. Cross-Origin Resource Sharing (CORS)**
```javascript
// Browser blocks this without CORS:
// Frontend (localhost:3100) → Backend (localhost:8000)
// Different ports = different origins!

// FastAPI CORS middleware allows it:
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3100"])
```

### **2. API Configuration**
```javascript
// Frontend can switch API endpoints
apiBaseUrl: 'http://localhost:8000',        // Local development
// apiBaseUrl: 'https://api.myapp.com',     // Production
```

### **3. Connection Status Tracking**
```javascript
// Alpine.js tracks connection status
connectionStatus: 'connected' | 'disconnected',

// Visual indicator in UI
<div :class="connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'">
```

### **4. Error Handling**
```javascript
// Proper error handling for network requests
try {
    const data = await this.makeApiRequest('/api/notes');
    this.connectionStatus = 'connected';
} catch (error) {
    this.connectionStatus = 'disconnected';
    this.error = `API Error: ${error.message}`;
}
```

## 🔍 Debugging Tips

### **Check CORS Issues**
Open browser dev tools (F12) → Console:
```
❌ Access to fetch at 'http://localhost:8000/api/notes' from origin 'http://localhost:3100' has been blocked by CORS policy
✅ No CORS errors = working correctly
```

### **Network Tab**
Dev Tools → Network → Look for:
- **Request URL**: `http://localhost:8000/api/notes`
- **Status**: `200 OK`
- **Response Headers**: `Access-Control-Allow-Origin: http://localhost:3100`

### **Console Logging**
The frontend logs all API requests:
```javascript
console.log('📡 API Request: GET http://localhost:8000/api/notes');
console.log('📡 API Response: 200 OK');
console.log('📊 Loaded 5 notes');
```

## 🚀 Production Deployment

### **Frontend (Static Site)**
```bash
# Build for production (if using build tools)
npm run build

# Deploy to Netlify, Vercel, or any static host
# Frontend URL: https://myapp.netlify.app
```

### **Backend (API Server)**
```python
# Update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.netlify.app"],  # Production frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Environment Variables**
```javascript
// Frontend config
const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? 'https://api.myapp.com'
    : 'http://localhost:8000';
```

## 💡 Why This Approach is Better

### **1. Real-World Architecture**
- Matches production setups (separate frontend/backend)
- Frontend can be deployed to CDN (faster)
- Backend can scale independently

### **2. Technology Flexibility**
- Frontend: Any framework (Alpine.js, React, Vue)
- Backend: Any API (FastAPI, Django, Node.js)
- Database: Any database technology

### **3. Development Benefits**
- Hot reload for frontend changes
- Independent debugging
- Team can work on frontend/backend separately

### **4. Alpine.js Learning**
- Pure client-side reactivity
- Real HTTP requests (not same-domain)
- Proper error handling and connection management

This setup gives you a realistic development environment that mirrors how modern web applications are actually built and deployed! 🎯