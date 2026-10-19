from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/docs")
    assert response.status_code == 200

def test_lexical_analysis_valid():
    payload = {"code": "x = 10\nprint(x)"}
    response = client.post("/api/lexical", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert len(data["tokens"]) > 0

def test_parse_code_valid():
    payload = {"code": "x = 10\nprint(x)"}
    response = client.post("/api/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ast"] is not None