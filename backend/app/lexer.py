"""Analisador léxico (scanner) do Mini-Python.

Lê o código-fonte caractere a caractere, agrupa os caracteres em lexemas e
classifica cada lexema em uma categoria de token. Espaços e comentários são
ignorados. Como o Python usa indentação para delimitar blocos, o scanner
também emite os tokens estruturais NOVA_LINHA, INDENTACAO e DESINDENTACAO.

O scanner NÃO interrompe a leitura ao encontrar um erro: ele registra o erro
(com linha e coluna) e continua, para que todos os problemas apareçam de uma vez.
"""

# ---------- categorias de token ----------
PALAVRA_RESERVADA = "PALAVRA_RESERVADA"
IDENTIFICADOR = "IDENTIFICADOR"
LITERAL_INTEIRO = "LITERAL_INTEIRO"
LITERAL_REAL = "LITERAL_REAL"
LITERAL_STRING = "LITERAL_STRING"
OPERADOR = "OPERADOR"
DELIMITADOR = "DELIMITADOR"
NOVA_LINHA = "NOVA_LINHA"
INDENTACAO = "INDENTACAO"
DESINDENTACAO = "DESINDENTACAO"

ESTRUTURAIS = {NOVA_LINHA, INDENTACAO, DESINDENTACAO}

# ---------- escopo léxico ----------
PALAVRAS_RESERVADAS = {
    "if", "elif", "else", "while", "def", "return", "print",
    "and", "or", "not", "True", "False", "None",
}
OPERADORES_DUPLOS = {"==", "!=", "<=", ">=", "//", "**", "+=", "-=", "*=", "/="}
OPERADORES_SIMPLES = set("+-*/%<>=")
DELIMITADORES = set("():,")


class CompilerError(Exception):
    """Erro léxico ou sintático, com posição no código-fonte."""

    def __init__(self, fase, mensagem, linha, coluna, lexema=""):
        super().__init__(mensagem)
        self.fase = fase
        self.phase = fase
        self.message = mensagem
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.lexema = lexema
        self.line = linha
        self.column = coluna

    def to_dict(self):
        return {
            "tipo": "ERRO_LEXICO" if self.fase == "léxico" else "ERRO_SINTATICO",
            "lexema": self.lexema,
            "linha": self.linha,
            "coluna": self.coluna,
            "mensagem": self.mensagem,
        }


def _token(tipo, lexema, linha, coluna):
    return {"tipo": tipo, "lexema": lexema, "linha": linha, "coluna": coluna}


def scan(source):
    """Executa o scanner e devolve (tokens, erros).

    Os erros têm o formato:
    {"tipo": "ERRO_LEXICO", "lexema": ..., "linha": ..., "coluna": ..., "mensagem": ...}
    """
    tokens = []
    erros = []
    indents = [0]
    text = source.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4)
    lines = text.split("\n")
    last_line = len(lines)

    def erro(mensagem, lexema, linha, coluna):
        erros.append(
            {
                "tipo": "ERRO_LEXICO",
                "lexema": lexema,
                "linha": linha,
                "coluna": coluna,
                "mensagem": mensagem,
            }
        )

    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip(" ")
        # Linhas em branco e de comentário não geram tokens.
        if stripped == "" or stripped.startswith("#"):
            continue

        indent = len(line) - len(stripped)
        if indent > indents[-1]:
            indents.append(indent)
            tokens.append(_token(INDENTACAO, "", lineno, 1))
        else:
            while indent < indents[-1]:
                indents.pop()
                tokens.append(_token(DESINDENTACAO, "", lineno, 1))
            if indent != indents[-1]:
                erro(
                    "Indentação inconsistente: o recuo desta linha não corresponde "
                    "a nenhum nível de indentação anterior.",
                    line[:indent],
                    lineno,
                    1,
                )

        i = indent
        n = len(line)
        while i < n:
            ch = line[i]
            col = i + 1

            if ch == " ":
                i += 1
            elif ch == "#":
                break  # comentário de linha: ignora o resto
            elif ch.isdigit():
                j = i
                while j < n and line[j].isdigit():
                    j += 1
                real = False
                if j + 1 < n and line[j] == "." and line[j + 1].isdigit():
                    real = True
                    j += 1
                    while j < n and line[j].isdigit():
                        j += 1
                if j < n and (line[j].isalpha() or line[j] == "_"):
                    while j < n and (line[j].isalnum() or line[j] == "_"):
                        j += 1
                    erro(
                        f"Número malformado '{line[i:j]}': um identificador "
                        "não pode começar com dígito.",
                        line[i:j],
                        lineno,
                        col,
                    )
                else:
                    tipo = LITERAL_REAL if real else LITERAL_INTEIRO
                    tokens.append(_token(tipo, line[i:j], lineno, col))
                i = j
            elif ch.isalpha() or ch == "_":
                j = i
                while j < n and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                palavra = line[i:j]
                tipo = PALAVRA_RESERVADA if palavra in PALAVRAS_RESERVADAS else IDENTIFICADOR
                tokens.append(_token(tipo, palavra, lineno, col))
                i = j
            elif ch in "\"'":
                j = i + 1
                fechada = False
                while j < n:
                    if line[j] == "\\":  # sequência de escape: pula o próximo caractere
                        j += 2
                        continue
                    if line[j] == ch:
                        fechada = True
                        break
                    j += 1
                if fechada:
                    tokens.append(_token(LITERAL_STRING, line[i:j + 1], lineno, col))
                    i = j + 1
                else:
                    erro(
                        f"String não terminada: as aspas {ch} abertas aqui "
                        "não foram fechadas na mesma linha.",
                        line[i:].rstrip(),
                        lineno,
                        col,
                    )
                    i = n
            elif line[i:i + 2] in OPERADORES_DUPLOS:
                tokens.append(_token(OPERADOR, line[i:i + 2], lineno, col))
                i += 2
            elif ch in OPERADORES_SIMPLES:
                tokens.append(_token(OPERADOR, ch, lineno, col))
                i += 1
            elif ch in DELIMITADORES:
                tokens.append(_token(DELIMITADOR, ch, lineno, col))
                i += 1
            elif ch == "!":
                erro(
                    "Operador incompleto '!': para comparar valores diferentes use '!='.",
                    "!",
                    lineno,
                    col,
                )
                i += 1
            else:
                erro(
                    f"Caractere não reconhecido '{ch}'. "
                    "Verifique se ele faz parte do subconjunto suportado.",
                    ch,
                    lineno,
                    col,
                )
                i += 1

        tokens.append(_token(NOVA_LINHA, "", lineno, n + 1))

    while len(indents) > 1:
        indents.pop()
        tokens.append(_token(DESINDENTACAO, "", last_line, 1))

    return tokens, erros


def tokenize(source):
    """Versão estrita: devolve os tokens ou levanta CompilerError no primeiro erro."""
    tokens, erros = scan(source)
    if erros:
        e = erros[0]
        raise CompilerError("léxico", e["mensagem"], e["linha"], e["coluna"], e["lexema"])
    return tokens