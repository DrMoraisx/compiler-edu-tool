
from dataclasses import dataclass, asdict

KEYWORDS = {
    "if", "else", "while", "for", "in", "def", "return",
    "print", "and", "or", "not", "True", "False", "None"
}

TWO_CHAR_OPERATORS = {
    "==", "!=", "<=", ">=", "**", "//", "+=", "-=", "*=", "/="
}

ONE_CHAR_OPERATORS = {"+", "-", "*", "/", "%", "=", "<", ">"}
DELIMITERS = {"(", ")", "[", "]", "{", "}", ":", ",", "."}


@dataclass
class Token:
    tipo: str
    lexema: str
    linha: int
    coluna: int

    def to_dict(self):
        return asdict(self)


@dataclass
class LexicalError:
    tipo: str
    lexema: str
    linha: int
    coluna: int
    mensagem: str

    def to_dict(self):
        return asdict(self)


def scan(source: str):
    """Analisa o código e retorna (tokens, erros)."""
    tokens = []
    errors = []
    i, line, col = 0, 1, 1
    n = len(source)

    def advance():
        nonlocal i, line, col
        ch = source[i]
        i += 1

        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1

        return ch

    while i < n:
        ch = source[i]

        if ch in " \t\r":
            advance()
            continue

        if ch == "\n":
            advance()
            continue

        start_line, start_col = line, col

        # Comentários iniciados por #.
        if ch == "#":
            while i < n and source[i] != "\n":
                advance()
            continue

        # Identificadores e palavras reservadas.
        if ch.isalpha() or ch == "_":
            start = i

            while i < n and (
                source[i].isalnum() or source[i] == "_"
            ):
                advance()

            lexeme = source[start:i]

            kind = (
                "PALAVRA_RESERVADA"
                if lexeme in KEYWORDS
                else "IDENTIFICADOR"
            )

            tokens.append(
                Token(kind, lexeme, start_line, start_col).to_dict()
            )
            continue

        # Literais inteiros e reais.
        if ch.isdigit():
            start = i

            while i < n and source[i].isdigit():
                advance()

            kind = "LITERAL_INTEIRO"

            if (
                i + 1 < n
                and source[i] == "."
                and source[i + 1].isdigit()
            ):
                advance()

                while i < n and source[i].isdigit():
                    advance()

                kind = "LITERAL_REAL"

            # Exemplo inválido: 12abc.
            if i < n and (
                source[i].isalpha() or source[i] == "_"
            ):
                while i < n and (
                    source[i].isalnum() or source[i] == "_"
                ):
                    advance()

                bad = source[start:i]

                errors.append(
                    LexicalError(
                        "ERRO_LEXICO",
                        bad,
                        start_line,
                        start_col,
                        f"Literal numérico inválido: '{bad}'."
                    ).to_dict()
                )
            else:
                tokens.append(
                    Token(
                        kind,
                        source[start:i],
                        start_line,
                        start_col
                    ).to_dict()
                )

            continue

        # Strings entre aspas simples ou duplas.
        if ch in ("'", '"'):
            quote = ch
            start = i
            advance()

            escaped = False
            closed = False

            while i < n:
                current = source[i]

                if current == "\n" and not escaped:
                    break

                advance()

                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == quote:
                    closed = True
                    break

            lexeme = source[start:i]

            if closed:
                tokens.append(
                    Token(
                        "LITERAL_STRING",
                        lexeme,
                        start_line,
                        start_col
                    ).to_dict()
                )
            else:
                errors.append(
                    LexicalError(
                        "ERRO_LEXICO",
                        lexeme,
                        start_line,
                        start_col,
                        f"String não terminada na linha "
                        f"{start_line}, coluna {start_col}."
                    ).to_dict()
                )

            continue

        # Verifica operadores compostos antes dos simples.
        pair = source[i:i + 2]

        if pair in TWO_CHAR_OPERATORS:
            advance()
            advance()

            tokens.append(
                Token(
                    "OPERADOR",
                    pair,
                    start_line,
                    start_col
                ).to_dict()
            )
            continue

        if ch in ONE_CHAR_OPERATORS:
            advance()

            tokens.append(
                Token(
                    "OPERADOR",
                    ch,
                    start_line,
                    start_col
                ).to_dict()
            )
            continue

        if ch in DELIMITERS:
            advance()

            tokens.append(
                Token(
                    "DELIMITADOR",
                    ch,
                    start_line,
                    start_col
                ).to_dict()
            )
            continue

        # Caractere desconhecido.
        advance()

        errors.append(
            LexicalError(
                "ERRO_LEXICO",
                ch,
                start_line,
                start_col,
                f"Caractere não reconhecido: '{ch}' "
                f"na linha {start_line}, coluna {start_col}."
            ).to_dict()
        )

    return tokens, errors
