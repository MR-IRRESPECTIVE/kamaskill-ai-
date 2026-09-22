import requests
import json

pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n>>\nendobj\n4 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(1. Intro) Tj\n100 650 Td\n(This is intro.) Tj\n100 600 Td\n(2. Body) Tj\n100 550 Td\n(This is body.) Tj\n100 500 Td\n(3. Concl) Tj\n100 450 Td\n(This is concl.) Tj\n100 400 Td\n(4. More) Tj\n100 350 Td\n(This is more.) Tj\n100 300 Td\n(5. End) Tj\n100 250 Td\n(This is end.) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000289 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n539\n%%EOF\n'

with open("test_sections.pdf", "wb") as f:
    f.write(pdf_content)

with open("test_sections.pdf", "rb") as f:
    files = {'file': ('test_sections.pdf', f, 'application/pdf')}
    try:
        res = requests.post('http://localhost:8000/materials/analyze-and-save?number_of_questions=5', files=files)
        print("STATUS", res.status_code)
        print("RESPONSE", res.text)
    except Exception as e:
        print(e)
