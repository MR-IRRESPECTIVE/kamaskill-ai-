import subprocess
import time
import requests
import os

env = os.environ.copy()
env['MOCK_GEMINI'] = 'true'

proc = subprocess.Popen([r'.\venv\Scripts\python.exe', '-m', 'uvicorn', 'main:app', '--port', '8001'], cwd='backend', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)

time.sleep(3) # wait for startup

# Create a small valid PDF file
pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n>>\nendobj\n4 0 obj\n<< /Length 53 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000289 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n392\n%%EOF\n'

with open("test.pdf", "wb") as f:
    f.write(pdf_content)

with open("test.pdf", "rb") as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    try:
        res = requests.post('http://localhost:8001/materials/analyze-and-save?number_of_questions=5', files=files)
        print("STATUS", res.status_code)
    except Exception as e:
        print(e)

proc.terminate()
stdout, _ = proc.communicate()
print("--- BACKEND LOGS ---")
print(stdout)
