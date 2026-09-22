import requests
import json

with open(r"backend\data_viz_guide.pdf", "rb") as f:
    files = {'file': ('data_viz_guide.pdf', f, 'application/pdf')}
    try:
        res = requests.post('http://localhost:8000/materials/analyze-and-save?number_of_questions=5', files=files)
        print("STATUS", res.status_code)
        print("RESPONSE", res.text)
    except Exception as e:
        print(e)
