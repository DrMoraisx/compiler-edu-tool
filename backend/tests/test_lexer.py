import pytest

from app.lexer import (
    DELIMITADORES,
    ESTRUTURAIS,
    OPERADORES_DUPLOS,
    OPERADORES_SIMPLES,
    PALAVRAS_RESERVADAS,
    CompilerError,
    scan,
    tokenize,
)


def significativos(tokens):
    """Tokens sem os estruturais (NOVA_LINHA, INDENTACAO, DESINDENTACAO)."""
    return [t for t in tokens if t["tipo"] not in ESTRUTURAIS]


def tipos(tokens):
    return [t["tipo"] for t in significativos(tokens)]


def lexemas(tokens):
    return [t["lexema"] for t in significativos(tokens)]


# ---------- formato do token ----------
def test_token_format():
    tokens, erros = scan("x = 10")
    assert erros == []
    assert tokens[0] == {"tipo": "IDENTIFICADOR", "lexema": "x", "linha": 1, "coluna": 1}


def test_assignment_tokens():
    tokens, erros = scan("numero = 10")
    assert erros == []
    assert tipos(tokens) == ["IDENTIFICADOR", "OPERADOR", "LITERAL_INTEIRO"]
    assert lexemas(tokens) == ["numero", "=", "10"]


# ---------- palavras reservadas ----------
@pytest.mark.parametrize("palavra", sorted(PALAVRAS_RESERVADAS))
def test_each_reserved_word_is_recognized(palavra):
    tokens, erros = scan(palavra)
    assert erros == []
    assert significativos(tokens) == [
        {"tipo": "PALAVRA_RESERVADA", "lexema": palavra, "linha": 1, "coluna": 1}
    ]


def test_reserved_word_prefix_is_an_identifier():
    # "iffy" e "printer" começam com palavra reservada, mas são identificadores
    tokens, _ = scan("iffy printer whiles")
    assert tipos(tokens) == ["IDENTIFICADOR"] * 3


def test_reserved_words_are_case_sensitive():
    tokens, _ = scan("true IF none")
    assert tipos(tokens) == ["IDENTIFICADOR"] * 3


# ---------- identificadores ----------
@pytest.mark.parametrize("nome", ["numero", "_x1", "resultado2", "a", "_", "soma_total", "área"])
def test_valid_identifiers(nome):
    tokens, erros = scan(nome)
    assert erros == []
    assert tipos(tokens) == ["IDENTIFICADOR"]
    assert lexemas(tokens) == [nome]


@pytest.mark.parametrize("invalido", ["1abc", "9_x", "12abc"])
def test_identifier_cannot_start_with_digit(invalido):
    tokens, erros = scan(invalido)
    assert tokens == [tokens[-1]]  # só o token estrutural NOVA_LINHA
    assert len(erros) == 1
    assert erros[0]["tipo"] == "ERRO_LEXICO"
    assert erros[0]["lexema"] == invalido
    assert "Número malformado" in erros[0]["mensagem"]


# ---------- literais ----------
@pytest.mark.parametrize("texto", ["0", "10", "42", "007"])
def test_integer_literals(texto):
    tokens, erros = scan(texto)
    assert erros == []
    assert significativos(tokens)[0]["tipo"] == "LITERAL_INTEIRO"
    assert lexemas(tokens) == [texto]


@pytest.mark.parametrize("texto", ["3.14", "0.5", "10.0", "123.456"])
def test_real_literals(texto):
    tokens, erros = scan(texto)
    assert erros == []
    assert significativos(tokens)[0]["tipo"] == "LITERAL_REAL"
    assert lexemas(tokens) == [texto]


@pytest.mark.parametrize("texto", ['"ola"', "'ola'", '""', '"com espaços e # hash"', '"aspas \\" escapadas"'])
def test_string_literals_keep_quotes_in_lexeme(texto):
    tokens, erros = scan(texto)
    assert erros == []
    assert tipos(tokens) == ["LITERAL_STRING"]
    assert lexemas(tokens) == [texto]


def test_hash_inside_string_is_not_a_comment():
    tokens, erros = scan('x = "a # b"  # comentario')
    assert erros == []
    assert lexemas(tokens) == ["x", "=", '"a # b"']


# ---------- operadores ----------
@pytest.mark.parametrize("op", sorted(OPERADORES_SIMPLES))
def test_single_char_operators(op):
    tokens, erros = scan(f"a {op} b")
    assert erros == []
    assert tipos(tokens) == ["IDENTIFICADOR", "OPERADOR", "IDENTIFICADOR"]
    assert lexemas(tokens)[1] == op


@pytest.mark.parametrize("op", sorted(OPERADORES_DUPLOS))
def test_compound_operators_are_a_single_token(op):
    tokens, erros = scan(f"a {op} b")
    assert erros == []
    assert tipos(tokens) == ["IDENTIFICADOR", "OPERADOR", "IDENTIFICADOR"]
    assert lexemas(tokens)[1] == op


def test_compound_operator_without_spaces():
    assert lexemas(scan("a<=b")[0]) == ["a", "<=", "b"]
    assert lexemas(scan("a==b")[0]) == ["a", "==", "b"]
    assert lexemas(scan("x+=1")[0]) == ["x", "+=", "1"]


# ---------- delimitadores ----------
@pytest.mark.parametrize("delim", sorted(DELIMITADORES))
def test_each_delimiter(delim):
    tokens, erros = scan(delim)
    assert erros == []
    assert tipos(tokens) == ["DELIMITADOR"]
    assert lexemas(tokens) == [delim]


# ---------- comentários e espaços em branco ----------
def test_line_comment_is_ignored():
    tokens, erros = scan("# so um comentario")
    assert tokens == [] and erros == []


def test_inline_comment_is_ignored():
    tokens, erros = scan("x = 1  # fim da linha")
    assert erros == []
    assert lexemas(tokens) == ["x", "=", "1"]


def test_whitespace_generates_no_tokens():
    tokens, _ = scan("x      =        1")
    assert lexemas(tokens) == ["x", "=", "1"]
    assert all(t["lexema"].strip() != "" for t in significativos(tokens))


def test_blank_lines_are_ignored():
    tokens, _ = scan("a = 1\n\n   \n\nb = 2")
    assert lexemas(tokens) == ["a", "=", "1", "b", "=", "2"]


def test_tabs_are_expanded():
    tokens, erros = scan("if x:\n\ty = 1")
    assert erros == []
    assert "INDENTACAO" in [t["tipo"] for t in tokens]


# ---------- indentação ----------
def test_indent_and_dedent_tokens():
    tokens, erros = scan("if x:\n    y = 1\nz = 2")
    assert erros == []
    seq = [t["tipo"] for t in tokens]
    assert seq.index("INDENTACAO") < seq.index("DESINDENTACAO")
    assert seq.count("INDENTACAO") == seq.count("DESINDENTACAO") == 1


def test_dedents_are_closed_at_end_of_file():
    tokens, _ = scan("if x:\n    if y:\n        z = 1")
    seq = [t["tipo"] for t in tokens]
    assert seq.count("INDENTACAO") == 2
    assert seq.count("DESINDENTACAO") == 2


def test_newline_token_at_end_without_trailing_newline():
    tokens, _ = scan("x = 1")
    assert tokens[-1]["tipo"] == "NOVA_LINHA"


# ---------- posição (linha e coluna) ----------
def test_positions_of_tokens():
    tokens, _ = scan("int_a = 10\n   \nbb = 2")
    por_lexema = {t["lexema"]: t for t in significativos(tokens)}
    assert (por_lexema["int_a"]["linha"], por_lexema["int_a"]["coluna"]) == (1, 1)
    assert (por_lexema["10"]["linha"], por_lexema["10"]["coluna"]) == (1, 9)
    assert (por_lexema["bb"]["linha"], por_lexema["bb"]["coluna"]) == (3, 1)


def test_positions_with_indentation():
    tokens, _ = scan("if x:\n    print(x)")
    printa = [t for t in tokens if t["lexema"] == "print"][0]
    assert (printa["linha"], printa["coluna"]) == (2, 5)


def test_positions_after_string():
    tokens, _ = scan('a = "xy" + b')
    b = [t for t in tokens if t["lexema"] == "b"][0]
    assert b["coluna"] == 12


# ---------- erros léxicos ----------
@pytest.mark.parametrize("caractere", ["@", "$", "?", "&", "|", "^", "~", "`", ";", "{", "}", "[", "]", "."])
def test_unrecognized_character(caractere):
    tokens, erros = scan(f"x = 1 {caractere} 2")
    assert len(erros) == 1
    assert erros[0] == {
        "tipo": "ERRO_LEXICO",
        "lexema": caractere,
        "linha": 1,
        "coluna": 7,
        "mensagem": erros[0]["mensagem"],
    }
    assert f"'{caractere}'" in erros[0]["mensagem"]
    assert "subconjunto suportado" in erros[0]["mensagem"]


def test_scanner_continues_after_error():
    tokens, erros = scan("a = 1 @ b = 2")
    assert len(erros) == 1
    # os tokens depois do erro continuam sendo reconhecidos
    assert lexemas(tokens) == ["a", "=", "1", "b", "=", "2"]


def test_multiple_errors_are_accumulated():
    tokens, erros = scan('preco = 10 @ 2\nnome = "sem fechar\nvalor = 12abc\nz = 5 $')
    assert [(e["linha"], e["coluna"]) for e in erros] == [(1, 12), (2, 8), (3, 9), (4, 7)]
    assert len(erros) == 4
    # a linha 4 ainda foi lida
    assert any(t["lexema"] == "z" for t in tokens)


def test_unterminated_string():
    tokens, erros = scan('x = "abc')
    assert len(erros) == 1
    assert erros[0]["lexema"] == '"abc'
    assert (erros[0]["linha"], erros[0]["coluna"]) == (1, 5)
    assert "String não terminada" in erros[0]["mensagem"]
    assert lexemas(tokens) == ["x", "="]


def test_unterminated_string_does_not_swallow_next_line():
    tokens, erros = scan('a = "abc\nb = 2')
    assert len(erros) == 1
    assert "b" in lexemas(tokens)


def test_lone_exclamation_mark():
    _, erros = scan("a ! b")
    assert len(erros) == 1
    assert "!=" in erros[0]["mensagem"]


def test_inconsistent_indentation():
    tokens, erros = scan("if x:\n        y = 1\n    z = 2")
    assert len(erros) == 1
    assert "Indentação inconsistente" in erros[0]["mensagem"]
    assert erros[0]["linha"] == 3


def test_errors_do_not_expose_internal_details():
    _, erros = scan("x = @")
    texto = str(erros)
    assert "Traceback" not in texto and "/app/" not in texto


# ---------- casos de borda ----------
def test_empty_source():
    assert scan("") == ([], [])


def test_only_whitespace():
    assert scan("   \n \t \n") == ([], [])


def test_only_comments():
    assert scan("# a\n# b\n   # c") == ([], [])


def test_token_at_end_of_file_without_newline():
    tokens, erros = scan("print(x)")
    assert erros == []
    assert lexemas(tokens) == ["print", "(", "x", ")"]


def test_windows_line_endings():
    tokens, erros = scan("a = 1\r\nb = 2\r\n")
    assert erros == []
    b = [t for t in tokens if t["lexema"] == "b"][0]
    assert b["linha"] == 2


def test_unicode_and_emoji_in_string_and_comment():
    tokens, erros = scan('msg = "olá 😀"  # ação ñ')
    assert erros == []
    assert lexemas(tokens) == ["msg", "=", '"olá 😀"']


def test_lexically_valid_but_syntactically_invalid_code_is_tokenized():
    # O scanner só reconhece tokens; a estrutura não é verificada aqui.
    tokens, erros = scan("if if if ) ( else = =")
    assert erros == []
    assert len(significativos(tokens)) == 8


def test_c_style_code_gets_lexical_errors_not_a_crash():
    tokens, erros = scan("int numero = 10;")
    assert [e["lexema"] for e in erros] == [";"]
    assert lexemas(tokens) == ["int", "numero", "=", "10"]


# ---------- tokenize (versão estrita) ----------
def test_tokenize_returns_tokens_when_valid():
    assert lexemas(tokenize("x = 1")) == ["x", "=", "1"]


def test_tokenize_raises_on_first_error():
    with pytest.raises(CompilerError) as exc:
        tokenize("x = 1 @ 2 $ 3")
    assert exc.value.fase == "léxico"
    assert (exc.value.linha, exc.value.coluna) == (1, 7)
    assert exc.value.to_dict()["tipo"] == "ERRO_LEXICO"