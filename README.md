# Operation Phantom PDF (Corporate Secrets)

**Category**: Web Exploitation / OSINT / Forensics (PDF Steganography)  
**Difficulty**: Hard  
**Points**: 450  

---

## Challenge Description (Player Prompt)

We intercepted the internal document portal for **RVCE Cyber Labs**. Intelligence suggests their Lead Security Architect stored a confidential audit memo containing highly classified vault credentials inside the portal.

However, even if you manage to bypass their public access controls and retrieve the confidential PDF, the actual secrets are hidden deep within the document's structure using advanced stream steganography and encryption.

Can you perform the required recon, break into the vault, and retrieve the flag?

**Flag Format**: `rvcectf{...}`

---

## Deployment Instructions

To run the challenge locally or host it on a CTF server:

### Option 1: Docker (Recommended)
```bash
cd challenge
docker build -t rvce-ctf-phantom-pdf .
docker run -p 5000:5000 rvce-ctf-phantom-pdf
```
Then visit `http://localhost:5000` in your browser.

### Option 2: Python Virtual Environment
```bash
cd challenge
pip install -r requirements.txt
python build_pdf.py  # Generates the challenge PDF artifact
python app.py        # Starts the web server on port 5000
```

---

## Progressive Hints (For Scoreboard)

* **Hint 1 (-50 pts)**: The document search bar filters by `access_level = 'Public'`. Can you use basic SQL injection to leak documents marked as `Confidential`? Be careful of decoy flags!
* **Hint 2 (-100 pts)**: Standard PDF readers won't show Object 7 because it is not listed in the page catalog. Inspect the raw PDF object structure. Notice that the stream is compressed with `FlateDecode` (zlib).
* **Hint 3 (-150 pts)**: The encryption passphrase requires combining the author's Project Codename with their Employee ID. Check the leaked PDF metadata to find the Employee ID, then find the specific employee card on the `/team` page.
