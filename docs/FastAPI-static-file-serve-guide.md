# FastAPI Static File Serving - Complete Guide

## 📁 Project Structure
```
note-app/
├── main.py                     # FastAPI backend
├── static/                     # Static files directory
│   ├── index.html             # Main AG-Grid version
│   ├── index-basic.html       # Your basic Alpine.js version
│   ├── style.css              # CSS files
│   └── app.js                 # JavaScript files
├── requirements.txt
└── notes.db                   # SQLite database
```

## 🔗 Access Methods

### **Method 1: Direct Static Access (Current)**
With `app.mount("/static", StaticFiles(directory="static"), name="static")`:

```
✅ http://localhost:8000/static/index-basic.html
✅ http://localhost:8000/static/style.css
✅ http://localhost:8000/static/app.js
```

**Pros:**
- Simple and direct
- No additional routes needed
- Good for CSS, JS, images

**Cons:**
- URLs include `/static/` prefix
- Less control over access

### **Method 2: Dedicated Routes (Recommended)**
Add specific routes for your HTML pages:

```python
@app.get("/")
async def serve_main_page():
    return FileResponse("static/index.html")

@app.get("/basic")  
async def serve_basic_page():
    return FileResponse("static/index-basic.html")
```

**Access URLs:**
```
✅ http://localhost:8000/          # Main version
✅ http://localhost:8000/basic     # Basic version
```

**Pros:**
- Clean URLs
- Can add logic (auth, logging, etc.)
- Better SEO and user experience

### **Method 3: Dynamic Page Serving**
```python
@app.get("/page/{page_name}")
async def serve_page(page_name: str):
    return FileResponse(f"static/{page_name}.html")
```

**Access URLs:**
```
✅ http://localhost:8000/page/index-basic
✅ http://localhost:8000/page/some-other-page
```

## 🛠️ Complete Setup Example

Here's how to modify your `main.py` to support multiple versions:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Note Taking App")

# Enable CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Mount static files (for CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve different HTML versions
@app.get("/")
async def serve_main():
    """Main version with AG-Grid"""
    return FileResponse("static/index.html")

@app.get("/basic")
async def serve_basic():
    """Basic Alpine.js version"""
    return FileResponse("static/index-basic.html")

@app.get("/demo")
async def serve_demo():
    """Demo or test version"""
    return FileResponse("static/index-demo.html")

# Your existing API routes
@app.get("/api/notes")
async def get_notes():
    # ... your existing code
    pass

@app.post("/api/notes")
async def create_note():
    # ... your existing code
    pass
```

## 🎯 What Happens with Static Mount

When you use `app.mount("/static", StaticFiles(directory="static"), name="static")`:

1. **FastAPI automatically serves** any file in the `static/` directory
2. **URL pattern**: `http://domain/static/{filename}`
3. **File mapping**:
   - `static/index-basic.html` → `http://localhost:8000/static/index-basic.html`
   - `static/style.css` → `http://localhost:8000/static/style.css`
   - `static/images/logo.png` → `http://localhost:8000/static/images/logo.png`

## 🚀 Best Practice Setup

**For your note-taking app, I recommend this approach:**

```python
# Mount static for assets (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dedicated routes for HTML pages
@app.get("/")
async def home():
    return FileResponse("static/index.html")  # AG-Grid version

@app.get("/basic")  
async def basic():
    return FileResponse("static/index-basic.html")  # Your basic version

@app.get("/compare")
async def compare():
    return FileResponse("static/compare.html")  # Side-by-side comparison
```

**This gives you:**
- Clean URLs: `/`, `/basic`, `/compare`
- Static assets still work: `/static/style.css`
- Easy to add more versions
- Can add middleware (auth, logging) later

## 📝 HTML File References

**In your HTML files, reference static assets like this:**

```html
<!-- In index-basic.html -->
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/app.js"></script>
</head>
<body>
    <!-- Your Alpine.js code -->
</body>
</html>
```

## 🔧 Testing Your Setup

1. **Start your FastAPI server:**
   ```bash
   python main.py
   ```

2. **Test all access methods:**
   ```bash
   # Method 1: Direct static access
   curl http://localhost:8000/static/index-basic.html
   
   # Method 2: Dedicated route (if you add it)
   curl http://localhost:8000/basic
   
   # Check static assets work
   curl http://localhost:8000/static/style.css
   ```

3. **In browser:**
   - `http://localhost:8000/` - Main version
   - `http://localhost:8000/static/index-basic.html` - Basic version (direct)
   - `http://localhost:8000/basic` - Basic version (clean URL, if you add the route)

## 💡 Pro Tip

Create a simple navigation menu in your main `index.html`:

```html
<div class="mb-4">
    <nav class="flex space-x-4">
        <a href="/" class="text-blue-500 hover:text-blue-700">AG-Grid Version</a>
        <a href="/basic" class="text-green-500 hover:text-green-700">Basic Version</a>
        <a href="/static/index-basic.html" class="text-purple-500 hover:text-purple-700">Direct Static</a>
    </nav>
</div>
```

This way users can easily switch between versions!