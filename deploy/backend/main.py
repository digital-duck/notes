from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# import os

from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import datetime
from contextlib import contextmanager

app = FastAPI(title="Note Taking API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "*"
        "http://localhost:3100", "http://127.0.0.1:3100", "http://0.0.0.0:3100"
    ],
    allow_credentials=True, # False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "notes.db"

def init_db():
    """Initialize the database with the notes table"""
    with sqlite3.connect(DATABASE_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS my_note (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_name TEXT NOT NULL,
                note_description TEXT,
                note_url TEXT,
                note_comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'user',
                updated_by TEXT DEFAULT 'user'
            )
        """)
        conn.commit()

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Pydantic models
class NoteCreate(BaseModel):
    note_name: str
    note_description: Optional[str] = ""
    note_url: Optional[str] = ""
    note_comment: Optional[str] = ""

class NoteUpdate(BaseModel):
    note_name: Optional[str] = None
    note_description: Optional[str] = None
    note_url: Optional[str] = None
    note_comment: Optional[str] = None

class Note(BaseModel):
    id: int
    note_name: str
    note_description: Optional[str]
    note_url: Optional[str]
    note_comment: Optional[str]
    created_at: str
    updated_at: str
    created_by: str
    updated_by: str

# Initialize database on startup
init_db()


@app.get("/api/notes", response_model=List[Note])
async def get_notes():
    """Fetch all notes
    """
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, note_name, note_description, note_url, note_comment,
                   created_at, updated_at, created_by, updated_by
            FROM my_note 
            ORDER BY updated_at DESC
        """)
        notes = [dict(note) for note in cursor.fetchall()]
        return notes

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    """Get a specific note by ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, note_name, note_description, note_url, note_comment,
                   created_at, updated_at, created_by, updated_by
            FROM my_note WHERE id = ?
        """, (note_id,))
        note = cursor.fetchone()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return dict(note)

@app.post("/api/notes", response_model=Note)
async def create_note(note: NoteCreate):
    """Create a new note"""
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO my_note (note_name, note_description, note_url, note_comment)
            VALUES (?, ?, ?, ?)
        """, (note.note_name, note.note_description, note.note_url, note.note_comment))
        note_id = cursor.lastrowid
        conn.commit()
        
        # Return the created note
        cursor = conn.execute("""
            SELECT id, note_name, note_description, note_url, note_comment,
                   created_at, updated_at, created_by, updated_by
            FROM my_note WHERE id = ?
        """, (note_id,))
        return dict(cursor.fetchone())

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note: NoteUpdate):
    """Update a specific note by ID"""
    with get_db() as conn:
        # Check if note exists
        cursor = conn.execute("SELECT id FROM my_note WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        if note.note_name is not None:
            update_fields.append("note_name = ?")
            update_values.append(note.note_name)
        if note.note_description is not None:
            update_fields.append("note_description = ?")
            update_values.append(note.note_description)
        if note.note_url is not None:
            update_fields.append("note_url = ?")
            update_values.append(note.note_url)
        if note.note_comment is not None:
            update_fields.append("note_comment = ?")
            update_values.append(note.note_comment)
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(note_id)
            
            query = f"UPDATE my_note SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
        
        # Return updated note
        cursor = conn.execute("""
            SELECT id, note_name, note_description, note_url, note_comment,
                   created_at, updated_at, created_by, updated_by
            FROM my_note WHERE id = ?
        """, (note_id,))
        return dict(cursor.fetchone())

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    """Delete a note"""
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM my_note WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Note not found")
        
        conn.execute("DELETE FROM my_note WHERE id = ?", (note_id,))
        conn.commit()
        return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)