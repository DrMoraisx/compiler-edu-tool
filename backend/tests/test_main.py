
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_and_health():
    resposta_raiz = client.get("/")
    resposta_api = client.get("/api/health")
    resposta_alias = client.get("/health")

    assert resposta_raiz.status_code == 200
    assert resposta_api.status_code == 200
    assert resposta_alias.status_code == 200

    assert resposta_api.json()["status"] == "ok"
    assert resposta_alias.json()["status"] == "ok"


def test_analysis_returns_tokens():
    response = client.post(
        "/api/parse",
        json={"code": "numero = 10"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sucesso"] is True
    assert data["success"] is True
    assert data["sucesso_lexico"] is True
    assert data["sucesso_sintatico"] is True

    assert [
        token["lexema"] for token in data["tokens"]
    ] == ["numero", "=", "10"]

    assert data["erros"] == []
    assert data["ast"]["tipo"] == "Programa"


def test_parser_receives_complete_token_sequence():
    response = client.post(
        "/api/parse",
        json={"code": "numero = 10"}
    )

    data = response.json()

    tipos = [
        token["tipo"]
        for token in data["tokens_parser"]
    ]

    assert "IDENTIFICADOR" in tipos
    assert "OPERADOR" in tipos
    assert "LITERAL_INTEIRO" in tipos
    assert "NOVA_LINHA" in tipos

    assert data["lexico"]["tokens"] == data["tokens_parser"]


def test_analyze_alias():
    response = client.post(
        "/api/analyze",
        json={"code": "print('oi')"}
    )

    assert response.status_code == 200
    assert response.json()["sucesso"] is True


def test_legacy_codigo_field_is_supported():
    response = client.post(
        "/api/parse",
        json={"codigo": "numero = 10"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recebido"] is True
    assert data["sucesso"] is True
    assert data["ast"]["tipo"] == "Programa"


def test_lexical_error_does_not_execute_parser():
    response = client.post(
        "/api/parse",
        json={"code": "x = @\ny = 2"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sucesso"] is False
    assert data["sucesso_lexico"] is False
    assert data["sucesso_sintatico"] is False
    assert data["sintatico_executado"] is False

    assert data["erros_lexicos"][0]["lexema"] == "@"
    assert data["ast"] is None
    assert len(data["tokens_parser"]) > 0


def test_syntax_error_returns_null_ast():
    response = client.post(
        "/api/parse",
        json={"code": "resultado = 10 +"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sucesso_lexico"] is True
    assert data["sucesso_sintatico"] is False
    assert data["sintatico_executado"] is True

    assert data["ast"] is None
    assert len(data["erros_sintaticos"]) > 0

    erro = data["erros_sintaticos"][0]

    assert erro["tipo"] == "ERRO_SINTATICO"
    assert erro["linha"] == 1
    assert erro["coluna"] > 0
    assert erro["mensagem"]


def test_grouped_contract_is_available():
    response = client.post(
        "/api/parse",
        json={"code": "x = 10"}
    )

    data = response.json()

    assert "lexico" in data
    assert "sintatico" in data

    assert data["lexico"]["sucesso"] is True
    assert data["sintatico"]["executado"] is True
    assert data["sintatico"]["sucesso"] is True

    assert data["sintatico"]["ast"]["tipo"] == "Programa"


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
    response = client.post(
        "/api/parse",
        json={}
    )

    assert response.status_code == 422


def test_unexpected_request_field_does_not_replace_code():
    response = client.post(
        "/api/parse",
        json={
            "code": "x = 10",
            "outro_campo": "valor"
        }
    )

    assert response.status_code == 200
    assert response.json()["sucesso"] is True
