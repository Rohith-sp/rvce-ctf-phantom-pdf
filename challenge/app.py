import os
import sqlite3
from flask import Flask, render_template, request, g

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctf_portal.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                access_level TEXT,
                file_path TEXT,
                author TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE team (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                bio TEXT
            )
        ''')
        
        # Insert initial public and confidential records
        cursor.execute("INSERT INTO documents (title, access_level, file_path, author) VALUES ('Public Welcome Guide', 'Public', '#', 'Admin')")
        cursor.execute("INSERT INTO documents (title, access_level, file_path, author) VALUES ('Internal Confidential Memo', 'Confidential', '/static/confidential_memo.pdf', 'Dr. Arthur Pendelton (EMP-8492)')")
        
        # Insert team members (OSINT recon target)
        cursor.execute("INSERT INTO team (name, role, bio) VALUES ('Alice Smith', 'System Administrator', 'Manages internal server infrastructure. Project TITAN-101.')")
        cursor.execute("INSERT INTO team (name, role, bio) VALUES ('Dr. Arthur Pendelton (EMP-8492)', 'Lead Security Architect', 'Specialist in secure PDF vaults and FlateDecode streams. Leading Project VANGUARD. Encryption passphrase protocol requires joining Project Code and Employee ID.')")
        cursor.execute("INSERT INTO team (name, role, bio) VALUES ('Bob Jones', 'Frontend Developer', 'UI/UX specialist. Project ORION-404.')")
        
        db.commit()

@app.route('/')
def index():
    return render_template('index.html', results=None)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    db = get_db()
    cursor = db.cursor()
    
    # Vulnerable SQL query allowing SQL injection
    query = f"SELECT title, access_level, file_path, author FROM documents WHERE title LIKE '%{q}%' AND access_level = 'Public'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except Exception as e:
        results = [{"title": "Database Error", "access_level": "Error", "file_path": "#", "author": str(e)}]
        
    return render_template('index.html', results=results, query=q)

@app.route('/team')
def team():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, role, bio FROM team")
    members = cursor.fetchall()
    return render_template('team.html', members=members)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
