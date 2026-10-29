"""Testes de implantação: verificam os serviços REAIS em execução.

Execute com a aplicação no ar (docker compose up -d):

    docker compose exec backend python -m pytest tests/test_deploy.py -v

Se os serviços não estiverem acessíveis, os testes são ignorados (skip).
"""
import json
import os
import urllib.error
import urllib.request

import pytest

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://frontend:3000")


def _reachable(url):
    try:
        urllib.request.urlopen(url, timeout=3)
        return True
    except Exception:
        return False


def _post(path, payload):
    request = urllib.request.Request(
        BACKEND_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


backend_up = pytest.mark.skipif(
    not _reachable(BACKEND_URL + "/health"), reason="backend não está acessível"
)
frontend_up = pytest.mark.skipif(
    not _reachable(FRONTEND_URL), reason="frontend não está acessível"
)


@backend_up
def test_backend_health():
    with urllib.request.urlopen(BACKEND_URL + "/health", timeout=5) as response:
        assert response.status == 200
        assert json.loads(response.read()) == {"status": "ok"}


@backend_up
def test_backend_receives_code_with_reference_payload():
    status, body = _post("/api/parse", {"codigo": "int numero = 10;"})
    assert status == 200
    assert body["recebido"] is True


@backend_up
def test_backend_rejects_empty_code():
    status, body = _post("/api/parse", {"codigo": ""})
    assert status == 400
    assert "Informe um código-fonte" in body["detail"]


@backend_up
def test_backend_full_analysis():
    status, body = _post("/api/parse", {"codigo": "x = 10\nprint(x)"})
    assert status == 200
    assert body["success"] is True
    assert body["ast"]["type"] == "Program"


@frontend_up
def test_frontend_serves_page():
    with urllib.request.urlopen(FRONTEND_URL, timeout=5) as response:
        assert response.status == 200
        assert b"root" in response.read()