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
    # Anti-Bot Protection: Block automated scraping bots and common scanner User-Agents
    ua = request.headers.get('User-Agent', '').lower()
    bot_signatures = ['curl', 'wget', 'python-requests', 'scrapy', 'sqlmap', 'nikto', 'burp', 'nmap', 'crawler', 'spider', 'bot', 'go-http-client', 'java/']
    if any(bot in ua for bot in bot_signatures):
        return render_template('gate.html', doc={"title": "Bot Attack Blocked", "file": "#", "question": ""}, doc_id=0, error="UNAUTHORIZED ACCESS ALERT: Automated bot scanning detected and rejected by perimeter WAF!", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False), 403

    # Block any direct URL attempts to grab PDF files bypassing the security gate
    if request.path.lower().endswith('.pdf'):
        return render_template('gate.html', doc={"title": "Security Violation", "file": request.path, "question": ""}, doc_id=0, error="UNAUTHORIZED ACCESS ALERT: Direct PDF retrieval blocked by firewall! Security breach logged.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False)

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
    
    # Block lazy single-letter search probes
    if len(q.strip()) == 1:
        return render_template('gate.html', doc={"title": "WAF Security Alarm", "file": "#", "question": ""}, doc_id=0, error=f"UNAUTHORIZED ACCESS ALERT: Lazy single-letter search probe ('{q.strip()}') detected by firewall! Triggering security siren.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False)
    
    # Advanced WAF blocking beginner shortcuts (*, comments, OR logic) exactly aligning with the diagnostic hint
    blocked_keywords = ['*', '--', '#', '/*', ' or ', '||', 'drop ', 'delete ', 'insert ', 'update ', 'alter ', 'exec ']
    for kw in blocked_keywords:
        if kw in q.lower():
            return render_template('gate.html', doc={"title": "WAF Security Alarm", "file": "#", "question": ""}, doc_id=0, error=f"UNAUTHORIZED ACCESS ALERT: Forbidden pattern ('{kw.strip()}') detected by firewall! Triggering security siren.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False)
            
    db = get_db()
    cursor = db.cursor()
    
    # Vulnerable SQL query structured to require commentless, asterisk-less UNION balancing
    query = f"SELECT title, access_level, file_path, author FROM documents WHERE access_level = 'Public' AND title LIKE '%{q}%'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if any(row['access_level'] in ['Confidential', 'Restricted'] for row in results):
            session['sqli_unlocked_vault'] = True
    except Exception as e:
        results = [{"title": "Database Error", "access_level": "Error", "file_path": "#", "author": str(e)}]
        
    return render_template('index.html', results=results, query=q)

@app.route('/download/<int:doc_id>', methods=['GET', 'POST'])
def download_gate(doc_id):
    if doc_id not in SECURITY_QUESTIONS:
        abort(404)
        
    # Prevent IDOR guessing: require SQLi discovery before accessing non-public document gates
    if doc_id > 2 and not session.get('sqli_unlocked_vault'):
        return render_template('gate.html', doc={"title": "Security Gate Locked", "file": f"/download/{doc_id}", "question": ""}, doc_id=0, error="UNAUTHORIZED ACCESS ALERT: Direct URL enumeration blocked! Confidential document gate IDs must be unlocked via SQL database querying.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False)
        
    doc = SECURITY_QUESTIONS[doc_id]
    error = None
    success = False
    
    if request.method == 'POST':
        user_ans = request.form.get('answer', '').strip().lower()
        if user_ans == doc['answer'].lower() or (doc['answer'] == 'man' and user_ans in ['man', 'middle']):
            success = True
            session[f'auth_doc_{doc_id}'] = True
        else:
            error = "UNAUTHORIZED ACCESS ALERT: Incorrect security authorization answer! Triggering security siren..."
            
    redirect_target = "https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq" if error else None
    return render_template('gate.html', doc=doc, doc_id=doc_id, error=error, redirect_url=redirect_target, success=success)

@app.route('/secure_fetch/<int:doc_id>')
def secure_fetch(doc_id):
    if doc_id not in SECURITY_QUESTIONS:
        abort(404)
        
    if doc_id > 2 and not session.get('sqli_unlocked_vault'):
        return render_template('gate.html', doc={"title": "Security Gate Locked", "file": f"/secure_fetch/{doc_id}", "question": ""}, doc_id=0, error="UNAUTHORIZED ACCESS ALERT: Direct URL enumeration blocked! Confidential document gate IDs must be unlocked via SQL database querying.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False)
        
    # Verify player passed the security gate challenge for this specific document
    if not session.get(f'auth_doc_{doc_id}'):
        doc = SECURITY_QUESTIONS[doc_id]
        return render_template('gate.html', doc=doc, doc_id=doc_id, error="UNAUTHORIZED ACCESS ALERT: Direct fetch bypass detected! Security breach logged.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False)
        
    doc = SECURITY_QUESTIONS[doc_id]
    return send_from_directory(VAULT_DIR, doc['file'], as_attachment=True, download_name=doc['file'])

@app.route('/team')
def team():
    members = [
        {"name": "Marcus Sterling", "empid": "EMP-4182", "role": "Cloud Infrastructure Architect", "department": "Cloud Systems", "bio": "Architecting multi-region AWS Kubernetes clusters and zero-trust service mesh networking. Lead on Project AETHER."},
        {"name": "Viktor Reznov", "empid": "EMP-7731", "role": "Malware Reverse Engineer", "department": "Threat Research", "bio": "Dissecting nation-state kernel rootkits, memory-resident payloads, and polymorphic C2 communication channels. Lead on Project CERBERUS."},
        {"name": "Alice Smith", "empid": "EMP-1042", "role": "Network Infrastructure Engineer", "department": "Core Operations", "bio": "Managing campus routing topology, VLAN subnets, and distributed firewall perimeter defenses. Lead on Project TITAN."},
        {"name": "Chloe Bennett", "empid": "EMP-2904", "role": "Identity & Access Specialist", "department": "Zero Trust IAM", "bio": "Enforcing OAuth2 token claims, SAML federation protocols, and hardware biometric MFA policies across enterprise portals. Lead on Project AEGIS."},
        {"name": "David Kim", "empid": "EMP-3391", "role": "Database Operations Specialist", "department": "Data Integrity", "bio": "Overseeing SQLite caching clusters and high-availability database replication heartbeats across division nodes. Lead on Project ORION."},
        {"name": "Lucas Thorne", "empid": "EMP-6029", "role": "DevSecOps Pipeline Engineer", "department": "Automated Security", "bio": "Integrating SAST/DAST scanner runners into continuous deployment workflows and managing container registry vulnerability signatures. Lead on Project VULCAN."},
        {"name": "Dr. Arthur Pendelton", "empid": "EMP-8492", "role": "Lead Security Architect", "department": "Cryptographic Systems", "bio": "Spearheading enterprise vault cryptography and automated metadata audit verification. Principal investigator for Project VANGUARD."},
        {"name": "Elena Rostova", "empid": "EMP-5520", "role": "Threat Intelligence Analyst", "department": "Offensive Security", "bio": "Monitoring external web application attack vectors and conducting continuous penetration testing against portal endpoints. Lead on Project HELIOS."},
        {"name": "Dr. Sophia Sterling", "empid": "EMP-1845", "role": "Quantum Cryptography Researcher", "department": "Advanced Research", "bio": "Evaluating post-quantum lattice encryption algorithms and securing internal communications against harvest-now-decrypt-later vectors. Lead on Project KRYPTON."},
        {"name": "Harrison Wells", "empid": "EMP-8812", "role": "Physical Security Director", "department": "Facilities & Hardware", "bio": "Monitoring badge access control logs, biometric server room locks, and SCADA sensor telemetry across laboratory facilities."},
        {"name": "Amara Chen", "empid": "EMP-3470", "role": "Incident Response Lead", "department": "SOC Operations", "bio": "Coordinating 24/7 triage teams, analyzing SIEM alert correlations, and conducting forensic timeline reconstruction during engagements. Lead on Project SPECTRE."},
        {"name": "Samantha Vance", "empid": "EMP-9104", "role": "IT Procurement Director", "department": "Infrastructure Finance", "bio": "Managing quarterly cloud hosting budgets, hardware server upgrades, and laboratory vendor compliance audits."}
    ]
    return render_template('team.html', members=members)

@app.errorhandler(404)
def unauthorized_or_missing_page(e):
    return render_template('gate.html', doc={"title": "Perimeter Alarm", "file": request.path, "question": ""}, doc_id=0, error=f"UNAUTHORIZED ACCESS ALERT: Endpoint ('{request.path}') blocked or invalid! Triggering security siren.", redirect_url="https://youtu.be/Z9oThmTT6j0?si=ifNay_E1kgFOF0tq", success=False), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
