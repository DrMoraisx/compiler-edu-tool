
from app.lexer import analisar_lexico
from app.parser import Parser


def analisar_codigo(codigo):
    resultado_lexico = analisar_lexico(codigo)

    assert resultado_lexico["erros"] == [], (
        f"Erros léxicos encontrados: {resultado_lexico['erros']}"
    )

    parser = Parser(resultado_lexico["tokens"])

    return parser.analisar()


def test_atribuicao_simples():
    resultado = analisar_codigo("x = 10")

    assert resultado["erros"] == []

    ast = resultado["ast"]

    assert ast["tipo"] == "Programa"
    assert ast["corpo"][0]["tipo"] == "Atribuicao"
    assert ast["corpo"][0]["identificador"] == "x"
    assert ast["corpo"][0]["valor"]["valor"] == "10"


def test_atribuicao_texto():
    resultado = analisar_codigo('nome = "Maria"')

    assert resultado["erros"] == []

    atribuicao = resultado["ast"]["corpo"][0]

    assert atribuicao["tipo"] == "Atribuicao"
    assert atribuicao["identificador"] == "nome"
    assert atribuicao["valor"]["tipo_valor"] == "texto"


def test_literal_real():
    resultado = analisar_codigo("preco = 3.14")

    assert resultado["erros"] == []

    valor = resultado["ast"]["corpo"][0]["valor"]

    assert valor["tipo"] == "Literal"
    assert valor["valor"] == "3.14"
    assert valor["tipo_valor"] == "numero"


def test_comando_print():
    resultado = analisar_codigo("print(10)")

    assert resultado["erros"] == []

    comando = resultado["ast"]["corpo"][0]

    assert comando["tipo"] == "Print"
    assert comando["expressao"]["valor"] == "10"


def test_soma():
    resultado = analisar_codigo("resultado = 10 + 5")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["tipo"] == "ExpressaoBinaria"
    assert expressao["operador"] == "+"


def test_precedencia_multiplicacao():
    resultado = analisar_codigo("resultado = 10 + 5 * 2")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["operador"] == "+"
    assert expressao["direita"]["operador"] == "*"


def test_precedencia_parenteses():
    resultado = analisar_codigo("resultado = (10 + 5) * 2")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["operador"] == "*"
    assert expressao["esquerda"]["operador"] == "+"


def test_associatividade_subtracao_esquerda():
    resultado = analisar_codigo("resultado = 20 - 5 - 3")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["operador"] == "-"
    assert expressao["esquerda"]["operador"] == "-"
    assert expressao["direita"]["valor"] == "3"


def test_associatividade_divisao_esquerda():
    resultado = analisar_codigo("resultado = 20 / 5 / 2")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["operador"] == "/"
    assert expressao["esquerda"]["operador"] == "/"
    assert expressao["direita"]["valor"] == "2"


def test_expressao_com_identificadores():
    resultado = analisar_codigo("resultado = x + y")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["operador"] == "+"
    assert expressao["esquerda"]["tipo"] == "Identificador"
    assert expressao["direita"]["tipo"] == "Identificador"


def test_numero_negativo():
    resultado = analisar_codigo("x = -10")

    assert resultado["erros"] == []

    valor = resultado["ast"]["corpo"][0]["valor"]

    assert valor["tipo"] == "ExpressaoUnaria"
    assert valor["operador"] == "-"


def test_condicional_if():
    codigo = (
        "idade = 20\n"
        "if idade >= 18:\n"
        "    print(\"Maior de idade\")"
    )

    resultado = analisar_codigo(codigo)

    assert resultado["erros"] == []

    condicional = resultado["ast"]["corpo"][1]

    assert condicional["tipo"] == "Condicional"
    assert condicional["condicao"]["operador"] == ">="
    assert len(condicional["corpo_if"]) == 1


def test_condicional_if_else():
    codigo = (
        "idade = 20\n"
        "if idade >= 18:\n"
        "    print(\"Maior de idade\")\n"
        "else:\n"
        "    print(\"Menor de idade\")"
    )

    resultado = analisar_codigo(codigo)

    assert resultado["erros"] == []

    condicional = resultado["ast"]["corpo"][1]

    assert condicional["tipo"] == "Condicional"
    assert len(condicional["corpo_if"]) == 1
    assert len(condicional["corpo_else"]) == 1

    assert condicional["corpo_if"][0]["tipo"] == "Print"
    assert condicional["corpo_else"][0]["tipo"] == "Print"


def test_condicionais_aninhados():
    codigo = (
        "x = 3\n"
        "if x > 0:\n"
        "    if x < 5:\n"
        "        print(x)\n"
        "    else:\n"
        "        print(\"maior\")\n"
        "else:\n"
        "    print(\"zero\")"
    )

    resultado = analisar_codigo(codigo)

    assert resultado["erros"] == []

    condicional_externo = resultado["ast"]["corpo"][1]

    assert condicional_externo["tipo"] == "Condicional"

    condicional_interno = condicional_externo["corpo_if"][0]

    assert condicional_interno["tipo"] == "Condicional"
    assert len(condicional_interno["corpo_if"]) == 1
    assert len(condicional_interno["corpo_else"]) == 1

    assert len(condicional_externo["corpo_else"]) == 1


def test_multiplas_atribuicoes():
    codigo = (
        "x = 10\n"
        "y = 5\n"
        "resultado = x + y"
    )

    resultado = analisar_codigo(codigo)

    assert resultado["erros"] == []
    assert len(resultado["ast"]["corpo"]) == 3


def test_erro_expressao_incompleta():
    codigo = "x = 10 +\nprint(x)"

    resultado = analisar_codigo(codigo)

    assert len(resultado["erros"]) > 0

    erro = resultado["erros"][0]

    assert erro["linha"] == 1
    assert erro["coluna"] == 9
    assert erro["encontrado"] == "\n"
    assert erro["esperado"]


def test_erro_operador_sem_valor():
    resultado = analisar_codigo("x = 5 *")

    assert len(resultado["erros"]) > 0


def test_erro_parenteses_nao_fechados():
    resultado = analisar_codigo("print((10 + 5)")

    assert len(resultado["erros"]) > 0


def test_erro_comando_nao_reconhecido():
    resultado = analisar_codigo("while x")

    assert len(resultado["erros"]) > 0


def test_erro_else_sem_if():
    resultado = analisar_codigo("else:")

    assert len(resultado["erros"]) > 0


def test_posicao_dos_nos_ast():
    resultado = analisar_codigo("x = 10")

    atribuicao = resultado["ast"]["corpo"][0]

    assert atribuicao["posicao"]["linha"] == 1
    assert atribuicao["posicao"]["coluna"] == 1


def test_programa_com_varias_linhas():
    codigo = (
        "x = 10\n"
        "y = 5\n"
        "resultado = x + y * 2\n"
        "print(resultado)"
    )

    resultado = analisar_codigo(codigo)

    assert resultado["erros"] == []
    assert len(resultado["ast"]["corpo"]) == 4


def test_programa_com_comentarios_e_linhas_vazias():
    codigo = (
        "# comentário inicial\n"
        "\n"
        "x = 10\n"
        "# comentário intermediário\n"
        "print(x)"
    )

    resultado = analisar_codigo(codigo)

    assert resultado["erros"] == []
    assert len(resultado["ast"]["corpo"]) == 2


def test_programa_vazio():
    resultado = analisar_codigo("")

    assert resultado["erros"] == []
    assert resultado["ast"]["tipo"] == "Programa"
    assert resultado["ast"]["corpo"] == []


def test_recuperacao_de_erros_em_linhas_diferentes():
    codigo = (
        "x =\n"
        "y =\n"
        "z = 10"
    )

    resultado = analisar_codigo(codigo)

    assert len(resultado["erros"]) >= 2

    assert resultado["erros"][0]["linha"] == 1
    assert resultado["erros"][1]["linha"] == 2


def test_operacao_com_modulo():
    resultado = analisar_codigo("resto = 10 % 3")

    assert resultado["erros"] == []

    expressao = resultado["ast"]["corpo"][0]["valor"]

    assert expressao["tipo"] == "ExpressaoBinaria"
    assert expressao["operador"] == "%"


def test_operadores_relacionais():
    operadores = [
        "==",
        "!=",
        "<",
        ">",
        "<=",
        ">="
    ]

    for operador in operadores:
        resultado = analisar_codigo(
            f"resultado = a {operador} b"
        )

        assert resultado["erros"] == []

        expressao = resultado["ast"]["corpo"][0]["valor"]

        assert expressao["operador"] == operador
