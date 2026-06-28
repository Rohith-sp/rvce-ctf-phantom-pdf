import os
import codecs

def make_pdf(filename, title, author, body_lines, subject_meta="Standard Corporate Document"):
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
<< /Length 400 >>
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
0000000750 00000 n 
trailer
<< /Size 7 /Root 1 0 R /Info 6 0 R >>
startxref
880
%%EOF
"""
    output_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'wb') as f:
        f.write(pdf_content.encode('latin1', errors='ignore'))

def create_all_pdfs():
    # 1. Public Design Guidelines
    make_pdf("design_v2.pdf", "Frontend Design Guidelines v2.4", "Bob Jones", [
        "Standard UI/UX color palettes and typography rules.",
        "Ensure all components follow the Outfit font layout.",
        "No confidential vault tokens are stored in this public document."
    ])
    
    # 2. Public Welcome Guide
    make_pdf("welcome.pdf", "Public Welcome Guide & Policies", "Admin", [
        "Welcome to the RVCE Cyber Labs portal.",
        "Please follow standard security protocols when accessing files.",
        "Contact IT support for access permission inquiries."
    ])

    # 3. Decoy Confidential Topology
    make_pdf("topology_q3.pdf", "Q3 Network Infrastructure Topology", "Alice Smith", [
        "Subnet masks and firewall VLAN configurations for Q3.",
        "Internal router gateways are restricted to IP 10.0.4.1.",
        "Note: Vault access keys have been migrated to the Security Architect."
    ], subject_meta="Network Diagram Decoy")

    # 4. Decoy Confidential DB Logs
    make_pdf("db_logs.pdf", "Database Cache Replication Logs", "David Kim", [
        "Replication sync heartbeat active across all nodes.",
        "0 critical database synchronization errors detected.",
        "Status: Healthy."
    ], subject_meta="DB Replication Logs")

    # 5. TRUE TARGET: Arthur's Confidential Memo
    osint_key = "VANGUARD-8492"
    flag = "rvcectf{un10n_sqli_t0_r0t13_pdf_m3t4d4t4}"
    rot13_cipher = codecs.encode(flag, 'rot_13')
    make_pdf("confidential_memo.pdf", "CONFIDENTIAL INTERNAL AUDIT MEMO", "Dr. Arthur Pendelton [EMP-8492]", [
        "Subject: Security Vault Passphrase & Encryption Audit",
        "",
        "Unseen upon the printed page,",
        "I hold the tale of birth and age.",
        "Find the Subject in my Properties deep,",
        "Then spin it thirteen steps to secrets keep."
    ], subject_meta=f"[Vault Protocol: {osint_key} Verified] -> ROT13 Cipher: {rot13_cipher}")

    # 6. Decoy Restricted Threat Report
    make_pdf("threat_report.pdf", "Threat Vector Analysis Report", "Elena Rostova", [
        "Analysis of perimeter external attack vectors.",
        "Recommended action: enforce strict WAF filtering on query parameters.",
        "No cryptographic flags present."
    ], subject_meta="Threat Report Q3")

    # 7. Decoy Restricted Financial Audit
    make_pdf("finance_q2.pdf", "Executive Financial Audit Q2", "Samantha Vance", [
        "Quarterly lab server procurement expenditures.",
        "Cloud hosting budget allocated to Render and AWS infrastructure.",
        "Audit status: Approved."
    ], subject_meta="Financial Audit")

    print("[+] Successfully generated all 7 authentic vault PDFs (Decoys + True Target)!")

if __name__ == "__main__":
    create_all_pdfs()
