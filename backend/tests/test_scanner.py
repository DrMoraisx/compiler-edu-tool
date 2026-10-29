
from app.scanner import scan


def test_keywords_and_identifiers():
    tokens, errors = scan("if valor_1 == True:")

    assert not errors
    assert [t["lexema"] for t in tokens] == [
        "if", "valor_1", "==", "True", ":"
    ]


def test_numbers_strings_and_operators():
    tokens, errors = scan(
        'x = 12\ny = 3.14\nprint("oi")'
    )

    assert not errors
    assert any(
        t["tipo"] == "LITERAL_INTEIRO"
        and t["lexema"] == "12"
        for t in tokens
    )
    assert any(
        t["tipo"] == "LITERAL_REAL"
        and t["lexema"] == "3.14"
        for t in tokens
    )
    assert any(
        t["tipo"] == "LITERAL_STRING"
        and t["lexema"] == '"oi"'
        for t in tokens
    )


def test_comments_and_whitespace():
    tokens, errors = scan(
        "  # comentário\nx = 1 # fim"
    )

    assert not errors
    assert [t["lexema"] for t in tokens] == [
        "x", "=", "1"
    ]


def test_token_positions():
    tokens, errors = scan("x = 1\n  y=2")

    assert not errors

    y = next(t for t in tokens if t["lexema"] == "y")

    assert y["linha"] == 2
    assert y["coluna"] == 3


def test_unknown_character():
    tokens, errors = scan("x = @\ny = 2")

    assert len(errors) == 1
    assert errors[0]["lexema"] == "@"
    assert errors[0]["linha"] == 1
    assert errors[0]["coluna"] == 5

    assert any(t["lexema"] == "y" for t in tokens)


def test_unclosed_string():
    tokens, errors = scan('print("sem fim)')

    assert errors
    assert "String não terminada" in errors[0]["mensagem"]


def test_empty_source():
    tokens, errors = scan("")

    assert tokens == []
    assert errors == []


def test_compound_operators_and_delimiters():
    source = "( ) [ ] { } : , . <= >= != += ** //"

    tokens, errors = scan(source)

    assert not errors

    lexemes = [t["lexema"] for t in tokens]

    for item in [
        "(", ")", "[", "]", "{", "}", ":",
        ",", ".", "<=", ">=", "!=", "+=", "**", "//"
    ]:
        assert item in lexemes
