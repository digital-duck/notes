
# Note Taking App - Setup Instructions
- https://claude.ai/chat/86bcb3bf-7e17-44c3-9a3d-3bc390cc1e14

## Project Structure
```
note-app/
├── main.py                 # FastAPI backend
├── static/
│   └── index.html          # Alpine.js frontend
├── requirements.txt        # Python dependencies
├── notes.db               # SQLite database (auto-created)
└── README.md              # This file
```

## Requirements (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
```

## Setup Instructions

### 1. Create Project Directory
```bash
mkdir note-app
cd note-app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn python-multipart
```

### 4. Create File Structure
```bash
mkdir static
# Copy main.py to project root
# Copy index.html to static/ folder
```

### 5. Run the Application
```bash
python main.py
```
or
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the Application
Open your browser and go to: http://localhost:8000

## How This Maps to Streamlit

### Database Operations
**Streamlit:**
```python
import sqlite3
conn = sqlite3.connect('notes.db')
df = pd.read_sql_query("SELECT * FROM my_note", conn)
st.dataframe(df)
```

**Alpine.js + FastAPI:**
- FastAPI handles database operations with context managers
- Alpine.js calls REST endpoints to get data
- Frontend displays data reactively

### Forms and Input
**Streamlit:**
```python
with st.form("note_form"):
    name = st.text_input("Note Name")
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Note")
    if submitted:
        # Save to database
```

**Alpine.js:**
- Form inputs bound with x-model
- Form submission handled with @submit.prevent
- Data sent to FastAPI endpoint

### State Management
**Streamlit:**
```python
if 'notes' not in st.session_state:
    st.session_state.notes = []
```

**Alpine.js:**
- State managed in Alpine.js data object
- Reactive updates when data changes
- No need for session state - client-side state

### Display and Interaction
**Streamlit:**
```python
for note in notes:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(note['note_name'])
    with col2:
        if st.button("Edit", key=f"edit_{note['id']}"):
            # Edit logic
    with col3:
        if st.button("Delete", key=f"delete_{note['id']}"):
            # Delete logic
```

**Alpine.js:**
- Template loops with x-for
- Event handlers with @click
- Conditional display with x-show

## Key Differences

### Streamlit Approach:
- Server-side rendering
- Page reloads on interaction
- Built-in components
- Session state management
- Great for data science prototyping

### Alpine.js + FastAPI Approach:
- Client-side reactivity
- No page reloads
- Custom HTML/CSS design
- REST API architecture
- Better for production web apps

## Deployment Options

### Development:
```bash
uvicorn main:app --reload
```

### Production:
- Use gunicorn with uvicorn workers
- Deploy to VPS, AWS, or similar
- Add nginx as reverse proxy
- Use environment variables for config

### Docker Option:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Next Steps
1. Add user authentication
2. Add search functionality
3. Add pagination for large datasets
4. Add file upload capabilities
5. Add export features (CSV, JSON)
6. Add categories/tags for notes


