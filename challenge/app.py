import os
import sqlite3
from flask import Flask, render_template, request, g, send_from_directory, abort, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'rvce_cyber_labs_secret_vault_key_x99'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctf_portal.db')
VAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vault')

# Dictionary storing Security Challenge Questions and Answers for each document
SECURITY_QUESTIONS = {
    1: {"question": "What is the HTTP status code for 'Not Found'?", "answer": "404", "file": "design_v2.pdf", "title": "Frontend Design Guidelines v2.4"},
    2: {"question": "What is the standard port number for unencrypted HTTP?", "answer": "80", "file": "welcome.pdf", "title": "Public Welcome Guide & Policies"},
    3: {"question": "What is the default port number for encrypted HTTPS?", "answer": "443", "file": "topology_q3.pdf", "title": "Q3 Network Infrastructure Topology"},
    4: {"question": "Which network protocol translates domain names into IP addresses? (3 letters)", "answer": "dns", "file": "db_logs.pdf", "title": "Database Cache Replication Logs"},
    5: {"question": "Which Linux command is used to change file or directory permissions?", "answer": "chmod", "file": "confidential_memo.pdf", "title": "Internal Security Architecture Review"},
    6: {"question": "In cybersecurity, what does the first 'M' stand for in a MITM attack?", "answer": "man", "file": "threat_report.pdf", "title": "Threat Vector Analysis Report"},
    7: {"question": "What is the 3-bit binary representation of the decimal number 5?", "answer": "101", "file": "finance_q2.pdf", "title": "Executive Financial Audit Q2"}
}

@app.before_request
def block_unauthorized_shortcuts():
    # Block any direct URL attempts to grab PDF files bypassing the security gate
    if request.path.lower().endswith('.pdf'):
        return render_template('gate.html', doc={"title": "Security Violation", "file": request.path, "question": ""}, doc_id=0, error="UNAUTHORIZED ACCESS ALERT: Direct PDF retrieval blocked by firewall! Security breach logged.", success=False)

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
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DROP TABLE IF EXISTS documents')
        cursor.execute('''
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                access_level TEXT,
                file_path TEXT,
                author TEXT
            )
        ''')
        
        # Populate vault with realistic mixture of Public, Confidential, and Restricted files
        docs = [
            ("Frontend Design Guidelines v2.4", "Public", "/download/1", "Bob Jones"),
            ("Public Welcome Guide & Policies", "Public", "/download/2", "Admin"),
            ("Q3 Network Infrastructure Topology", "Confidential", "/download/3", "Alice Smith"),
            ("Database Cache Replication Logs", "Confidential", "/download/4", "David Kim"),
            ("Internal Security Architecture Review", "Confidential", "/download/5", "Dr. Arthur Pendelton"),
            ("Threat Vector Analysis Report", "Restricted", "/download/6", "Elena Rostova"),
            ("Executive Financial Audit Q2", "Restricted", "/download/7", "Samantha Vance")
        ]
        
        cursor.executemany('INSERT INTO documents (title, access_level, file_path, author) VALUES (?, ?, ?, ?)', docs)
        db.commit()

@app.route('/')
def index():
    return render_template('index.html', results=None)

@app.route('/search', methods=['GET', 'POST'])
def search():
    q = request.values.get('q', '')
    
    # Strict WAF Filter (Blocks comments, equality, OR boolean logic, forcing clean UNION SELECT)
    blocked_keywords = ['--', '#', '/*', '=', '1=1', 'true', ' or ', '||', 'union all']
    for kw in blocked_keywords:
        if kw in q.lower():
            return render_template('index.html', results=[{"title": "⚠️ WAF Security Alert", "access_level": "Blocked", "file_path": "#", "author": f"Firewall detected prohibited pattern: '{kw.strip()}'"}], query=q)
            
    db = get_db()
    cursor = db.cursor()
    
    # Vulnerable SQL query (UNION SELECT required to leak confidential records)
    query = f"SELECT title, access_level, file_path, author FROM documents WHERE title LIKE '%{q}%' AND access_level = 'Public'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except Exception as e:
        results = [{"title": "Database Error", "access_level": "Error", "file_path": "#", "author": str(e)}]
        
    return render_template('index.html', results=results, query=q)

@app.route('/download/<int:doc_id>', methods=['GET', 'POST'])
def download_gate(doc_id):
    if doc_id not in SECURITY_QUESTIONS:
        abort(404)
        
    doc = SECURITY_QUESTIONS[doc_id]
    error = None
    success = False
    
    if request.method == 'POST':
        user_ans = request.form.get('answer', '').strip().lower()
        if user_ans == doc['answer'].lower() or (doc['answer'] == 'man' and user_ans in ['man', 'middle']):
            success = True
            session[f'auth_doc_{doc_id}'] = True
        else:
            error = "UNAUTHORIZED ACCESS ALERT: Security breach logged. Redirecting to home portal..."
            
    return render_template('gate.html', doc=doc, doc_id=doc_id, error=error, success=success)

@app.route('/secure_fetch/<int:doc_id>')
def secure_fetch(doc_id):
    if doc_id not in SECURITY_QUESTIONS:
        abort(404)
        
    # Verify player passed the security gate challenge for this specific document
    if not session.get(f'auth_doc_{doc_id}'):
        doc = SECURITY_QUESTIONS[doc_id]
        return render_template('gate.html', doc=doc, doc_id=doc_id, error="UNAUTHORIZED ACCESS ALERT: Direct fetch bypass detected! Security breach logged.", success=False)
        
    doc = SECURITY_QUESTIONS[doc_id]
    return send_from_directory(VAULT_DIR, doc['file'], as_attachment=True, download_name=doc['file'])

@app.route('/team')
def team():
    members = [
        {"name": "Dr. Arthur Pendelton", "empid": "EMP-8492", "role": "Lead Security Architect", "department": "Cryptographic Systems", "bio": "Spearheading enterprise vault cryptography and automated metadata audit verification. Principal investigator for Project VANGUARD."},
        {"name": "Alice Smith", "empid": "EMP-1042", "role": "Network Infrastructure Engineer", "department": "Core Operations", "bio": "Managing campus routing topology, VLAN subnets, and distributed firewall perimeter defenses. Lead on Project TITAN."},
        {"name": "David Kim", "empid": "EMP-3391", "role": "Database Operations Specialist", "department": "Data Integrity", "bio": "Overseeing SQLite caching clusters and high-availability database replication heartbeats across division nodes. Lead on Project ORION."},
        {"name": "Elena Rostova", "empid": "EMP-5520", "role": "Threat Intelligence Analyst", "department": "Offensive Security", "bio": "Monitoring external web application attack vectors and conducting continuous penetration testing against portal endpoints. Lead on Project HELIOS."},
        {"name": "Samantha Vance", "empid": "EMP-9104", "role": "IT Procurement Director", "department": "Infrastructure Finance", "bio": "Managing quarterly cloud hosting budgets, hardware server upgrades, and laboratory vendor compliance audits."}
    ]
    return render_template('team.html', members=members)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
