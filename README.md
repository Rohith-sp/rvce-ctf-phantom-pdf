# Operation Phantom PDF (Corporate Secrets)

**Category**: Web Security / OSINT / Forensics  
**Difficulty**: Hard (Medium Web + Easy/Medium Forensics)  
**Points**: 450  

---

## Challenge Description (Player Prompt)

We intercepted the internal document portal for **RVCE Cyber Labs**. Intelligence suggests their Lead Security Architect stored a confidential audit memo containing highly classified vault credentials inside the portal.

However, even if you manage to bypass their public access controls and retrieve the confidential PDF, the actual secrets are hidden behind a poetic riddle and classic stream encoding.

Can you perform the required recon, break into the vault, and retrieve the flag?

**Access Challenge at**: `https://rvce-ctf-phantom-pdf.onrender.com`  
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

* **Hint 1 (-50 pts)**: The document search bar has a basic firewall blocking `=`, `--`, `#`, and `OR`. Try using a `UNION SELECT` query with `LIKE` to bypass the firewall and leak documents marked as `Confidential`.
* **Hint 2 (-100 pts)**: Once downloaded, open the confidential memo and read the poetic riddle carefully: *"Seek the Subject of my Properties to spin the cipher thirteen steps around."*
* **Hint 3 (-150 pts)**: Open the PDF's Document Properties / Metadata (or use `strings` / `exiftool`) to look at the `/Subject` field. You will see a ROT13 encoded cipher string! Decode it by rotating 13 steps.
