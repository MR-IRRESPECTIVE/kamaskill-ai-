import requests
files = {'file': ('test.pdf', b'fake pdf content', 'application/pdf')}
res = requests.post('http://localhost:8000/materials/analyze-and-save?number_of_questions=5', files=files)
print(res.status_code)
print(res.text)
