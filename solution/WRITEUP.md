# Solution Writeup: Operation Phantom PDF

## Overview & Architecture
This challenge combines **Medium-Hard Web Exploitation (UNION SQLi + Security Gate Bypass)**, **OSINT Reconnaissance across Decoys**, and **Poetic PDF Metadata Forensics (ROT13)**. Additionally, the challenge includes **AI Agent Traps** designed to mislead automated LLM solvers or naive grep scripts.

---

## Step-by-Step Walkthrough

### 1. Web Exploitation (UNION SELECT SQLi Evasion)
Accessing the document portal at `/`, we observe a search input that queries public documents.
The endpoint enforces a custom WAF blocking common keywords (`--`, `#`, `/*`, `=`, `1=1`, `or`).
To bypass the WAF and leak confidential records without using equal signs or comments, we craft a 4-column `UNION SELECT` payload using `LIKE`:
```sql
%' UNION SELECT title, access_level, file_path, author FROM documents WHERE access_level LIKE '%
```
Submitting this via POST leaks the entire enterprise vault consisting of **7 distinct documents** (Public, Confidential, and Restricted). Because there are multiple confidential documents (network diagrams, database logs, security reviews), players must determine which one holds the actual flag.

### 2. OSINT Reconnaissance (Filtering Decoys)
Navigating to `/team` (Team Directory), we observe the division roster and a global security policy stating that personnel access protocols follow `[ProjectCode]-[EmployeeID]`.
Reading the staff bios reveals that **Dr. Arthur Pendelton (`EMP-8492`)** is the Lead Security Architect handling enterprise vault cryptography. His project codename is `VANGUARD`.
Matching this back to our SQL injection query results, we locate Arthur's specific document: **"Internal Security Architecture Review"** (`/download/5`).

### 3. Security Password Gate Bypass
Clicking download on `/download/5` does not directly serve the file. Instead, it presents a **Security Access Control Challenge** asking a general knowledge tech question:
> *Which Linux command is used to change file or directory permissions?*

Answering **`chmod`** unlocks the security gate and downloads `confidential_memo.pdf`. *(Note: All other 6 decoy PDFs have different general knowledge questions such as HTTP status codes, DNS acronyms, or HTTPS port numbers)*.

### 4. PDF Verse & Metadata Forensics
Opening `confidential_memo.pdf` displays a poetic verse written on the memo:
```text
Unseen upon the printed page,
I hold the tale of birth and age.
Find the Subject in my Properties deep,
Then spin it thirteen steps to secrets keep.
```
This verse instructs the player to inspect the document's unseen metadata properties (specifically the **Subject** field) and spin it **thirteen steps** (ROT13).

Opening Document Properties in any PDF viewer (or running `strings confidential_memo.pdf` / `exiftool`) reveals the Subject attribute:
```text
Subject: [Vault Protocol: VANGUARD-8492 Verified] -> ROT13 Cipher: eiprpgs{ha10a_fdyv_g0_e0g13_cqs_z3g4q4g4}
```
Notice that the metadata verifies our OSINT key `VANGUARD-8492` and provides the ROT13 encoded string.

### 5. ROT13 Decryption & Flag Extraction
Taking the ROT13 cipher string `eiprpgs{ha10a_fdyv_g0_e0g13_cqs_z3g4q4g4}` and rotating each letter by 13 positions (via CyberChef, rot13.com, or Python) decodes the true flag:

**`rvcectf{un10n_sqli_t0_r0t13_pdf_m3t4d4t4}`**

---

## Verification
Run the automated deterministic solver:
```bash
python solution/solve.py
```
**Output**:
```text
[*] CHALLENGE VERIFIED SOLVED! True Flag retrieved: rvcectf{un10n_sqli_t0_r0t13_pdf_m3t4d4t4}
```
