from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
print(client.get("/competencies/employee/1").json())
