import os
import codecs

def make_pdf(filename, title, author, body_lines, subject_meta="Standard Corporate Document", keywords_meta="RVCE Cyber Labs"):
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>
endobj
5 0 obj
<< /Length 450 >>
stream
BT
/F1 18 Tf
50 700 Td
({title}) Tj
0 -30 Td
/F1 12 Tf
(Author: {author}) Tj
0 -25 Td
"""
    for line in body_lines:
        pdf_content += f"({line}) Tj\n0 -20 Td\n"
        
    pdf_content += f"""ET
endstream
endobj
6 0 obj
<<
  /Title ({title})
  /Author ({author})
  /Subject ({subject_meta})
  /Keywords ({keywords_meta})
  /Producer (RVCE Cyber Labs Vault System)
>>
endobj
xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000052 00000 n 
0000000109 00000 n 
0000000220 00000 n 
0000000288 00000 n 
0000000800 00000 n 
trailer
<< /Size 7 /Root 1 0 R /Info 6 0 R >>
startxref
940
%%EOF
"""
    output_dir = os.path.join(os.path.dirname(__file__), 'vault')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'wb') as f:
        f.write(pdf_content.encode('latin1', errors='ignore'))

def create_all_pdfs():
    # Single YouTube Link Base64 Decoy hidden cleanly inside Keywords metadata without 'decoy' labeling
    b64_yt = "aHR0cHM6Ly95b3V0dS5iZS9aOW9UaG1UVDZqMD9zaT11QS1KbWZIUURjaUg0Y3hN"

    # 1. Public Design Guidelines
    make_pdf("design_v2.pdf", "Frontend Design Guidelines v2.4", "Bob Jones", [
        "Standard UI/UX color palettes and typography rules.",
        "Ensure all components follow the Outfit font layout.",
        "Refer to portal documentation for visual guidelines."
    ], keywords_meta=f"Visual Reference Stream: {b64_yt}")
    
    # 2. Public Welcome Guide
    make_pdf("welcome.pdf", "Public Welcome Guide & Policies", "Admin", [
        "Welcome to the RVCE Cyber Labs portal.",
        "Please follow standard security protocols when accessing files.",
        "Contact IT support for access permission inquiries."
    ], keywords_meta=f"Orientation Media Mirror: {b64_yt}")

    # 3. Decoy Confidential Topology (References subtle decoy image diagram)
    make_pdf("topology_q3.pdf", "Q3 Network Infrastructure Topology", "Alice Smith", [
        "Subnet masks and firewall VLAN configurations for Q3.",
        "Internal router gateways are restricted to IP 10.0.4.1.",
        "Refer to schematic diagram hosted at /static/system_blueprint.png for perimeter gateways."
    ], subject_meta="Network Diagram Specification", keywords_meta=f"Network Telemetry Stream: {b64_yt}")

    # 4. Decoy Confidential DB Logs (Contains realistic fake token in Subject)
    make_pdf("db_logs.pdf", "Database Cache Replication Logs", "David Kim", [
        "Replication sync heartbeat active across all nodes.",
        "0 critical database synchronization errors detected.",
        "Backup log mirror synchronization verified."
    ], subject_meta="Sync Heartbeat Key: rvcectf{sql1t3_c4ch3_r3pl1c4t10n_k3y}", keywords_meta=f"Database Replication Mirror: {b64_yt}")

    # 5. TRUE TARGET: Arthur's Confidential Memo (Multi-layer encryption: ROT13 then XOR with VANGUARD-8492)
    osint_key = "VANGUARD-8492"
    flag = "rvcectf{un10n_sqli_t0_x0r_r0t13_m3t4d4t4}"
    rot13_cipher = codecs.encode(flag, 'rot_13')
    xored_bytes = bytes([ord(c) ^ ord(osint_key[i % len(osint_key)]) for i, c in enumerate(rot13_cipher)])
    hex_token = xored_bytes.hex()
    
    make_pdf("confidential_memo.pdf", "CONFIDENTIAL INTERNAL AUDIT MEMO", "Dr. Arthur Pendelton", [
        "Subject: Security Vault Passphrase & Encryption Audit",
        "",
        "Unseen upon the printed page,",
        "I hold the tale of birth and age.",
        "Find the Subject hex in Properties deep,",
        "XOR with my Project Code, then thirteen steps to secrets keep."
    ], subject_meta=f"Encrypted Verification Token: {hex_token}", keywords_meta=f"Internal Video Archive: {b64_yt}")

    # 6. Decoy Restricted Threat Report (Contains realistic fake token in body)
    make_pdf("threat_report.pdf", "Threat Vector Analysis Report", "Elena Rostova", [
        "Analysis of perimeter external attack vectors.",
        "Recommended action: enforce strict WAF filtering on query parameters.",
        "Captured C2 Malware Beacon Signature: rvcectf{m4lw4r3_b34c0n_s1gn4tur3_q3}"
    ], subject_meta="Threat Analysis Q3", keywords_meta=f"Captured Telemetry Log: {b64_yt}")

    # 7. Decoy Restricted Financial Audit (Contains realistic fake voucher in Subject)
    make_pdf("finance_q2.pdf", "Executive Financial Audit Q2", "Samantha Vance", [
        "Quarterly lab server procurement expenditures.",
        "Cloud hosting budget allocated to Render and AWS infrastructure.",
        "Quarterly fiscal balance approved."
    ], subject_meta="Fiscal Voucher Code: rvcectf{f1n4nc14l_v0uch3r_4ud1t}", keywords_meta=f"Fiscal Expenditure Archive: {b64_yt}")

    print("[+] Successfully generated all 7 authentic vault PDFs with realistic decoy flags and multi-layer cryptography!")

if __name__ == "__main__":
    create_all_pdfs()
