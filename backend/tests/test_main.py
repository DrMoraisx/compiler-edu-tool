
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_and_health():
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json()["status"] == "ok"


def test_analysis_returns_tokens():
    response = client.post(
        "/api/parse",
        json={"code": "numero = 10"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sucesso"] is True
    assert [
        token["lexema"] for token in data["tokens"]
    ] == ["numero", "=", "10"]

    assert data["erros"] == []


def test_analyze_alias():
    response = client.post(
        "/api/analyze",
        json={"code": "print('oi')"}
    )

    assert response.status_code == 200
    assert response.json()["sucesso"] is True


def test_lexical_error():
    response = client.post(
        "/api/parse",
        json={"code": "x = @\ny = 2"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sucesso"] is False
    assert data["erros"][0]["lexema"] == "@"


def test_empty_code():
    response = client.post(
        "/api/parse",
        json={"code": ""}
    )

    assert response.status_code == 400


def test_whitespace_code():
    response = client.post(
        "/api/parse",
        json={"code": "  \n "}
    )

    assert response.status_code == 400


def test_invalid_request():
    response = client.post("/api/parse", json={})

    assert response.status_code == 422
