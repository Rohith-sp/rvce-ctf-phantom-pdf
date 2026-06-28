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
                empid TEXT,
                role TEXT,
                department TEXT,
                bio TEXT
            )
        ''')
        
        # Insert initial public and confidential records
        cursor.execute("INSERT INTO documents (title, access_level, file_path, author) VALUES ('Public Welcome Guide & Policies', 'Public', '#', 'Admin')")
        cursor.execute("INSERT INTO documents (title, access_level, file_path, author) VALUES ('Q3 Network Infrastructure Topology', 'Public', '#', 'Alice Smith')")
        cursor.execute("INSERT INTO documents (title, access_level, file_path, author) VALUES ('Frontend Design Guidelines v2.4', 'Public', '#', 'Bob Jones')")
        cursor.execute("INSERT INTO documents (title, access_level, file_path, author) VALUES ('Internal Confidential Memo', 'Confidential', '/static/confidential_memo.pdf', 'Dr. Arthur Pendelton (EMP-8492)')")
        
        # Insert team members (Blended realistic OSINT targets)
        team_members = [
            ('Alice Smith', 'EMP-1042', 'Principal Cloud Architect', 'Infrastructure & DevOps', 'Oversees AWS and multi-cloud server clusters. Currently focused on automating zero-downtime CI/CD pipelines under Project TITAN-101.'),
            ('Bob Jones', 'EMP-3391', 'Lead UI/UX Designer', 'Frontend Engineering', 'Passionate about glassmorphism, micro-animations, and responsive accessibility. Spearheading design systems for Project ORION-404.'),
            ('Samantha Vance', 'EMP-6104', 'VP of Product Strategy', 'Executive Management', 'Coordinating cross-department milestones and client relations. Driving user engagement metrics across Europe and North America under Project HELIOS-881.'),
            ('David Kim', 'EMP-7728', 'Senior Database Engineer', 'Data Storage', 'Optimizing distributed SQL querying engines and high-availability caching. Managing storage protocols for Project CYBER-303.'),
            ('Dr. Arthur Pendelton', 'EMP-8492', 'Lead Security Architect', 'Cyber Defense Labs', 'Specializes in document steganography, encrypted stream vaults, and zero-trust authentication. Leading research on Project VANGUARD.'),
            ('Elena Rostova', 'EMP-9012', 'Threat Intelligence Analyst', 'Security Operations', 'Monitors AP threat vectors, network anomalies, and malware heuristics. Coordinating defensive counter-measures for Project NEXUS-550.')
        ]
        
        for m in team_members:
            cursor.execute("INSERT INTO team (name, empid, role, department, bio) VALUES (?, ?, ?, ?, ?)", m)
        
        db.commit()

@app.route('/')
def index():
    return render_template('index.html', results=None)

@app.route('/search', methods=['GET', 'POST'])
def search():
    q = request.values.get('q', '')
    
    # Custom Medium-Hard WAF Filter (Blocks comments, equal signs, and naive payloads)
    blocked_keywords = ['--', '#', '/*', '=', '1=1', 'true']
    for kw in blocked_keywords:
        if kw in q.lower():
            return render_template('index.html', results=[{"title": "⚠️ WAF Security Alert", "access_level": "Blocked", "file_path": "#", "author": f"Firewall detected prohibited pattern: '{kw.strip()}'"}], query=q)
            
    db = get_db()
    cursor = db.cursor()
    
    # Vulnerable SQL query (Medium-Hard SQLi required to leak records)
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
    cursor.execute("SELECT name, empid, role, department, bio FROM team")
    members = cursor.fetchall()
    return render_template('team.html', members=members)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
