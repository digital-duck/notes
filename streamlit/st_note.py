import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
import os

# Page configuration
st.set_page_config(
    page_title="Note Taking App - Streamlit",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
DATABASE_URL = "streamlit_notes.db"

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

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
                created_by TEXT DEFAULT 'streamlit_user',
                updated_by TEXT DEFAULT 'streamlit_user'
            )
        """)
        conn.commit()

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'selected_note_id' not in st.session_state:
        st.session_state.selected_note_id = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'note_name': '',
            'note_description': '',
            'note_url': '',
            'note_comment': ''
        }

@st.cache_data
def load_notes():
    """Load all notes from database with caching"""
    with get_db() as conn:
        query = """
            SELECT id, note_name, note_description, note_url, note_comment,
                   created_at, updated_at, created_by, updated_by
            FROM my_note 
            ORDER BY updated_at DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

def create_note(note_name, note_description, note_url, note_comment):
    """Create a new note"""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO my_note (note_name, note_description, note_url, note_comment)
            VALUES (?, ?, ?, ?)
        """, (note_name, note_description, note_url, note_comment))
        conn.commit()
    # Clear cache to refresh data
    load_notes.clear()

def update_note(note_id, note_name, note_description, note_url, note_comment):
    """Update an existing note"""
    with get_db() as conn:
        conn.execute("""
            UPDATE my_note 
            SET note_name = ?, note_description = ?, note_url = ?, note_comment = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (note_name, note_description, note_url, note_comment, note_id))
        conn.commit()
    # Clear cache to refresh data
    load_notes.clear()

def delete_note(note_id):
    """Delete a note"""
    with get_db() as conn:
        conn.execute("DELETE FROM my_note WHERE id = ?", (note_id,))
        conn.commit()
    # Clear cache to refresh data
    load_notes.clear()

def get_note_by_id(note_id):
    """Get a specific note by ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, note_name, note_description, note_url, note_comment,
                   created_at, updated_at, created_by, updated_by
            FROM my_note WHERE id = ?
        """, (note_id,))
        result = cursor.fetchone()
        return dict(result) if result else None

def reset_form():
    """Reset form and session state"""
    st.session_state.selected_note_id = None
    st.session_state.edit_mode = False
    st.session_state.form_data = {
        'note_name': '',
        'note_description': '',
        'note_url': '',
        'note_comment': ''
    }

def main():
    """Main application function"""
    # Initialize database and session state
    init_db()
    init_session_state()
    
    # Header
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">📝 Note Taking App</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                Built with Streamlit + SQLite
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load notes data
    df = load_notes()
    
    # Sidebar for form
    with st.sidebar:
        st.markdown("### 📝 Note Form")
        
        # Show current mode
        if st.session_state.edit_mode and st.session_state.selected_note_id:
            st.info(f"🎯 **Editing Mode**\nNote ID: {st.session_state.selected_note_id}")
            
            # Load selected note data if not already loaded
            if not any(st.session_state.form_data.values()):
                selected_note = get_note_by_id(st.session_state.selected_note_id)
                if selected_note:
                    st.session_state.form_data = {
                        'note_name': selected_note['note_name'] or '',
                        'note_description': selected_note['note_description'] or '',
                        'note_url': selected_note['note_url'] or '',
                        'note_comment': selected_note['note_comment'] or ''
                    }
        else:
            st.success("✨ **Create Mode**\nFill form to add new note")
        
        # Form
        with st.form("note_form", clear_on_submit=True):
            note_name = st.text_input(
                "Note Name *", 
                value=st.session_state.form_data['note_name'],
                help="Required field"
            )
            
            note_url = st.text_input(
                "Note URL", 
                value=st.session_state.form_data['note_url'],
                placeholder="https://example.com"
            )
            
            note_description = st.text_area(
                "Description", 
                value=st.session_state.form_data['note_description'],
                height=100
            )
            
            note_comment = st.text_area(
                "Comments", 
                value=st.session_state.form_data['note_comment'],
                height=80
            )
            
            # Form buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.edit_mode:
                    submit_button = st.form_submit_button("💾 Update Note", type="primary")
                else:
                    submit_button = st.form_submit_button("➕ Create Note", type="primary")
            
            with col2:
                cancel_button = st.form_submit_button("🔄 Reset Form")
            
            # Handle form submission
            if submit_button:
                if not note_name.strip():
                    st.error("Note name is required!")
                else:
                    try:
                        if st.session_state.edit_mode and st.session_state.selected_note_id:
                            # Update existing note
                            update_note(
                                st.session_state.selected_note_id,
                                note_name, note_description, note_url, note_comment
                            )
                            st.success("✅ Note updated successfully!")
                            reset_form()
                            st.rerun()  # Refresh the page
                        else:
                            # Create new note
                            create_note(note_name, note_description, note_url, note_comment)
                            st.success("✅ Note created successfully!")
                            reset_form()
                            st.rerun()  # Refresh the page
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if cancel_button:
                reset_form()
                st.rerun()
    
    # Main content area
    st.markdown("### 📊 Notes Database")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Notes", len(df))
    with col2:
        notes_with_url = len(df[df['note_url'].notna() & (df['note_url'] != '')])
        st.metric("With URLs", notes_with_url)
    with col3:
        notes_with_desc = len(df[df['note_description'].notna() & (df['note_description'] != '')])
        st.metric("With Description", notes_with_desc)
    with col4:
        if len(df) > 0:
            latest_date = pd.to_datetime(df['updated_at']).max().strftime('%m/%d/%y')
            st.metric("Last Updated", latest_date)
        else:
            st.metric("Last Updated", "N/A")
    
    if len(df) > 0:
        # Search and filter
        st.markdown("#### 🔍 Search & Filter")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "Search notes", 
                placeholder="Search by name, description, or comment...",
                label_visibility="collapsed"
            )
        
        with col2:
            show_only_with_url = st.checkbox("Only show notes with URLs")
        
        # Filter dataframe
        filtered_df = df.copy()
        
        if search_term:
            mask = (
                filtered_df['note_name'].str.contains(search_term, case=False, na=False) |
                filtered_df['note_description'].str.contains(search_term, case=False, na=False) |
                filtered_df['note_comment'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if show_only_with_url:
            filtered_df = filtered_df[filtered_df['note_url'].notna() & (filtered_df['note_url'] != '')]
        
        st.markdown(f"#### 📋 Notes Table ({len(filtered_df)} records)")
        
        # Display dataframe with selection
        if len(filtered_df) > 0:
            # Create display dataframe with formatted columns
            display_df = filtered_df.copy()
            
            # Format timestamps
            display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%m/%d/%y %H:%M')
            display_df['updated_at'] = pd.to_datetime(display_df['updated_at']).dt.strftime('%m/%d/%y %H:%M')
            
            # Truncate long text for better display
            display_df['note_description'] = display_df['note_description'].apply(
                lambda x: (x[:100] + '...') if pd.notna(x) and len(str(x)) > 100 else x
            )
            display_df['note_comment'] = display_df['note_comment'].apply(
                lambda x: (x[:50] + '...') if pd.notna(x) and len(str(x)) > 50 else x
            )
            
            # Column configuration for better display
            column_config = {
                "id": st.column_config.NumberColumn("ID", width="small"),
                "note_name": st.column_config.TextColumn("Name", width="medium"),
                "note_description": st.column_config.TextColumn("Description", width="large"),
                "note_url": st.column_config.LinkColumn("URL", width="medium"),
                "note_comment": st.column_config.TextColumn("Comment", width="medium"),
                "created_at": st.column_config.DatetimeColumn("Created", width="small"),
                "updated_at": st.column_config.DatetimeColumn("Updated", width="small"),
            }
            
            # Data editor for selection and editing
            edited_df = st.data_editor(
                display_df,
                column_config=column_config,
                use_container_width=True,
                num_rows="dynamic",
                disabled=["id", "created_at", "updated_at", "created_by", "updated_by"],
                key="notes_editor"
            )
            
            # Action buttons
            st.markdown("#### ⚡ Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            # Select note for editing
            with col1:
                selected_rows = st.multiselect(
                    "Select note to edit",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: f"ID {x}: {filtered_df[filtered_df['id']==x]['note_name'].iloc[0][:30]}...",
                    max_selections=1
                )
                
                if selected_rows:
                    if st.button("✏️ Edit Selected", type="secondary"):
                        st.session_state.selected_note_id = selected_rows[0]
                        st.session_state.edit_mode = True
                        st.session_state.form_data = {
                            'note_name': '',
                            'note_description': '',
                            'note_url': '',
                            'note_comment': ''
                        }  # Will be loaded in sidebar
                        st.rerun()
            
            # Delete functionality
            with col2:
                delete_id = st.selectbox(
                    "Select note to delete",
                    options=[None] + filtered_df['id'].tolist(),
                    format_func=lambda x: "Choose note..." if x is None else f"ID {x}: {filtered_df[filtered_df['id']==x]['note_name'].iloc[0][:20]}...",
                )
                
                if delete_id:
                    if st.button("🗑️ Delete Note", type="secondary"):
                        if st.session_state.get('confirm_delete') == delete_id:
                            try:
                                delete_note(delete_id)
                                st.success(f"✅ Note {delete_id} deleted!")
                                if st.session_state.selected_note_id == delete_id:
                                    reset_form()
                                st.session_state.confirm_delete = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting note: {str(e)}")
                        else:
                            st.session_state.confirm_delete = delete_id
                            st.warning("⚠️ Click again to confirm deletion")
            
            # Export functionality
            with col3:
                if st.button("📥 Export CSV"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"notes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            # Refresh data
            with col4:
                if st.button("🔄 Refresh Data"):
                    load_notes.clear()
                    st.rerun()
        
        else:
            st.info("🔍 No notes match your search criteria")
    
    else:
        st.info("📝 No notes yet. Use the sidebar form to create your first note!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>📝 Streamlit Note Taking App | Built with ❤️ using Streamlit & SQLite</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()