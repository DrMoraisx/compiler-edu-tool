
"""Testes de implantação com os serviços reais em execução.

Execute com o Docker Compose ativo:

    docker compose exec backend pytest tests/test_deploy.py -vv

Os testes verificam:
- Saúde do backend.
- Recebimento de código pela API.
- Rejeição de código vazio.
- Análise léxica e sintática completa.
- Disponibilidade do frontend.

Se um serviço não estiver acessível, os testes correspondentes
serão ignorados (SKIPPED), e não contabilizados como aprovados.
"""

import json
import os
import urllib.error
import urllib.request

import pytest


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://frontend:3000"
)


def requisitar_get(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.status, response.read()


def requisitar_post(url, payload):
    requisicao = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            requisicao,
            timeout=10
        ) as response:
            return response.status, json.loads(
                response.read()
            )

    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read())


def backend_esta_disponivel():
    try:
        requisitar_get(BACKEND_URL + "/health")
        return True
    except Exception:
        return False


def frontend_esta_disponivel():
    try:
        requisitar_get(FRONTEND_URL)
        return True
    except Exception:
        return False


backend_up = pytest.mark.skipif(
    not backend_esta_disponivel(),
    reason="Backend não está acessível."
)

frontend_up = pytest.mark.skipif(
    not frontend_esta_disponivel(),
    reason="Frontend não está acessível."
)


@backend_up
def test_backend_health():
    status, conteudo = requisitar_get(
        BACKEND_URL + "/health"
    )

    dados = json.loads(conteudo)

    assert status == 200
    assert dados["status"] == "ok"


@backend_up
def test_backend_receives_code_with_reference_payload():
    status, dados = requisitar_post(
        BACKEND_URL + "/api/parse",
        {
            "codigo": "numero = 10"
        }
    )

    assert status == 200
    assert dados["recebido"] is True
    assert dados["sucesso_lexico"] is True
    assert dados["sucesso_sintatico"] is True


@backend_up
def test_backend_rejects_empty_code():
    status, dados = requisitar_post(
        BACKEND_URL + "/api/parse",
        {
            "codigo": ""
        }
    )

    assert status == 400
    assert "Informe um código-fonte" in dados["detail"]


@backend_up
def test_backend_full_analysis():
    status, dados = requisitar_post(
        BACKEND_URL + "/api/parse",
        {
            "code": (
                "numero = 10\n"
                "resultado = numero * 2\n"
                "print(resultado)"
            )
        }
    )

    assert status == 200
    assert dados["sucesso"] is True
    assert dados["sucesso_lexico"] is True
    assert dados["sucesso_sintatico"] is True
    assert dados["ast"]["tipo"] == "Programa"
    assert len(dados["tokens"]) > 0


@backend_up
def test_backend_syntax_error_returns_null_ast():
    status, dados = requisitar_post(
        BACKEND_URL + "/api/parse",
        {
            "code": "resultado = numero *"
        }
    )

    assert status == 200
    assert dados["sucesso_lexico"] is True
    assert dados["sucesso_sintatico"] is False
    assert dados["ast"] is None
    assert len(dados["erros_sintaticos"]) > 0


@backend_up
def test_backend_lexical_error_does_not_execute_parser():
    status, dados = requisitar_post(
        BACKEND_URL + "/api/parse",
        {
            "code": "numero = 10 @ 2"
        }
    )

    assert status == 200
    assert dados["sucesso_lexico"] is False
    assert dados["sintatico_executado"] is False
    assert dados["ast"] is None
    assert len(dados["erros_lexicos"]) > 0


@frontend_up
def test_frontend_serves_page():
    status, conteudo = requisitar_get(FRONTEND_URL)

    assert status == 200
    assert b"root" in conteudo
