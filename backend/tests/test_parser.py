import pytest

from app.lexer import CompilerError, tokenize
from app.parser import Parser


def parse(src):
    return Parser(tokenize(src)).parse()


def test_assignment():
    ast = parse("x = 10")
    stmt = ast["body"][0]
    assert stmt["type"] == "Assignment"
    assert stmt["variable"] == "x"
    assert stmt["value"] == {"type": "Literal", "kind": "number", "value": 10}


def test_operator_precedence():
    expr = parse("r = 1 + 2 * 3")["body"][0]["value"]
    assert expr["operator"] == "+"
    assert expr["right"]["operator"] == "*"


def test_parentheses_override_precedence():
    expr = parse("r = (1 + 2) * 3")["body"][0]["value"]
    assert expr["operator"] == "*"
    assert expr["left"]["operator"] == "+"


def test_division_and_unary_minus():
    expr = parse("r = -4 / 2")["body"][0]["value"]
    assert expr["operator"] == "/"
    assert expr["left"]["type"] == "UnaryExpression"


def test_print_with_string_and_multiple_args():
    stmt = parse('print("soma:", 1 + 2)')["body"][0]
    assert stmt["type"] == "PrintStatement"
    assert len(stmt["arguments"]) == 2
    assert stmt["arguments"][0]["kind"] == "string"


def test_if_else():
    src = "if x > 1:\n    print(1)\nelse:\n    print(2)\ny = 3"
    ast = parse(src)
    assert len(ast["body"]) == 2  # if e a atribuição seguinte
    node = ast["body"][0]
    assert node["type"] == "IfStatement"
    assert node["condition"]["operator"] == ">"
    assert len(node["body"]) == 1
    assert len(node["orelse"]) == 1


def test_elif_becomes_nested_if():
    src = "if a:\n    x = 1\nelif b:\n    x = 2\nelse:\n    x = 3"
    node = parse(src)["body"][0]
    assert node["orelse"][0]["type"] == "IfStatement"
    assert len(node["orelse"][0]["orelse"]) == 1


def test_function_definition_with_body():
    src = "def soma(a, b):\n    return a + b\nr = soma(1, 2)"
    ast = parse(src)
    func = ast["body"][0]
    assert func["type"] == "FunctionDef"
    assert func["params"] == ["a", "b"]
    assert func["body"][0]["type"] == "ReturnStatement"
    assert ast["body"][1]["value"]["type"] == "CallExpression"


def test_nested_blocks():
    src = "if a:\n    if b:\n        print(1)\n    print(2)\nprint(3)"
    ast = parse(src)
    outer = ast["body"][0]
    assert len(outer["body"]) == 2
    assert outer["body"][0]["type"] == "IfStatement"
    assert len(ast["body"]) == 2


def test_empty_program_with_only_comments():
    assert parse("# nada aqui")["body"] == []


@pytest.mark.parametrize(
    "src, fragment, line",
    [
        ("x = ", "Esperada uma expressão", 1),
        ("if x > 1\n    print(1)", "Esperado ':'", 1),
        ("if x:\nprint(1)", "bloco indentado", 2),
        ("print(1", "Esperado ')'", 1),
        ("else:\n    x = 1", "sem um 'if'", 1),
        ("x = 1\n    y = 2", "Indentação inesperada", 2),
        ("def f(a,):\n    return a", "nome de um parâmetro", 1),
        ("x = 1 2", "Esperado fim da linha", 1),
    ],
)
def test_syntax_errors(src, fragment, line):
    with pytest.raises(CompilerError) as exc:
        parse(src)
    assert exc.value.phase == "sintático"
    assert fragment in exc.value.message
    assert exc.value.line == line