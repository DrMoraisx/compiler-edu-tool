"""Analisador sintático (descendente recursivo) do Mini-Python.

PRÉVIA da Etapa 4: já existe no backend (endpoint /api/syntax), mas ainda não
faz parte da interface nem do contrato da Etapa 3 (análise léxica).
Cobre apenas o subconjunto abaixo (sem while, and/or/not, True/False/None,
%, //, ** e operadores compostos).

Gramática:

    programa   -> comando* EOF
    comando    -> print | if | def | return | atribuicao | expressao  (NOVA_LINHA)
    bloco      -> NOVA_LINHA INDENTACAO comando+ DESINDENTACAO
    if         -> 'if' expr ':' bloco ('elif' expr ':' bloco)* ('else' ':' bloco)?
    def        -> 'def' ID '(' [ID (',' ID)*] ')' ':' bloco
    return     -> 'return' [expr]
    print      -> 'print' '(' [expr (',' expr)*] ')'
    atribuicao -> ID '=' expr
    expr       -> soma (('==' | '!=' | '<' | '>' | '<=' | '>=') soma)*
    soma       -> termo (('+' | '-') termo)*
    termo      -> unario (('*' | '/') unario)*
    unario     -> '-' unario | primario
    primario   -> NUMERO | STRING | ID | ID '(' args ')' | '(' expr ')'
"""

from .lexer import CompilerError

COMPARISON_OPS = {"==", "!=", "<", ">", "<=", ">="}


class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        if not self.tokens or self.tokens[-1]["tipo"] != "EOF":
            ultima = self.tokens[-1]["linha"] if self.tokens else 1
            self.tokens.append({"tipo": "EOF", "lexema": "", "linha": ultima, "coluna": 1})
        self.pos = 0

    # ---------- utilidades ----------
    def peek(self, offset=0):
        index = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[index]

    def advance(self):
        token = self.tokens[self.pos]
        if token["tipo"] != "EOF":
            self.pos += 1
        return token

    def check(self, tipo, lexema=None, offset=0):
        token = self.peek(offset)
        return token["tipo"] == tipo and (lexema is None or token["lexema"] == lexema)

    def match(self, tipo, lexema=None):
        if self.check(tipo, lexema):
            return self.advance()
        return None

    @staticmethod
    def describe(token):
        tipo = token["tipo"]
        if tipo == "EOF":
            return "fim do arquivo"
        if tipo == "NOVA_LINHA":
            return "fim da linha"
        if tipo == "INDENTACAO":
            return "indentação inesperada"
        if tipo == "DESINDENTACAO":
            return "fim do bloco"
        return f"'{token['lexema']}'"

    def error(self, message, token=None):
        token = token or self.peek()
        return CompilerError(
            "sintático", message, token["linha"], token["coluna"], token["lexema"]
        )

    def expect(self, tipo, lexema=None, what=None):
        token = self.peek()
        if self.check(tipo, lexema):
            return self.advance()
        wanted = what or (f"'{lexema}'" if lexema else tipo)
        raise self.error(
            f"Esperado {wanted}, mas encontrou {self.describe(token)}.", token
        )

    def expect_newline(self):
        token = self.peek()
        if token["tipo"] == "NOVA_LINHA":
            self.advance()
            return
        raise self.error(
            f"Esperado fim da linha, mas encontrou {self.describe(token)}.", token
        )

    # ---------- programa e comandos ----------
    def parse(self):
        body = []
        while not self.check("EOF"):
            body.append(self.statement())
        return {"type": "Program", "body": body}

    def statement(self):
        token = self.peek()
        tipo, lexema = token["tipo"], token["lexema"]

        if tipo == "INDENTACAO":
            raise self.error("Indentação inesperada.", token)
        if tipo == "PALAVRA_RESERVADA":
            if lexema == "print":
                return self.print_statement()
            if lexema == "if":
                return self.if_statement()
            if lexema == "def":
                return self.def_statement()
            if lexema == "return":
                return self.return_statement()
            if lexema in ("else", "elif"):
                raise self.error(f"'{lexema}' sem um 'if' correspondente.", token)
        if tipo == "IDENTIFICADOR" and self.check("OPERADOR", "=", offset=1):
            return self.assignment()

        expr = self.expression()
        self.expect_newline()
        return {"type": "ExpressionStatement", "expression": expr, "line": token["linha"]}

    def block(self):
        self.expect("NOVA_LINHA", what="quebra de linha após ':'")
        self.expect("INDENTACAO", what="um bloco indentado")
        body = []
        while not self.check("DESINDENTACAO") and not self.check("EOF"):
            body.append(self.statement())
        self.expect("DESINDENTACAO")
        return body

    def print_statement(self):
        token = self.advance()
        self.expect("DELIMITADOR", "(")
        args = []
        if not self.check("DELIMITADOR", ")"):
            args.append(self.expression())
            while self.match("DELIMITADOR", ","):
                args.append(self.expression())
        self.expect("DELIMITADOR", ")")
        self.expect_newline()
        return {"type": "PrintStatement", "arguments": args, "line": token["linha"]}

    def if_statement(self):
        token = self.advance()  # 'if' ou 'elif'
        condition = self.expression()
        self.expect("DELIMITADOR", ":")
        body = self.block()
        orelse = []
        if self.check("PALAVRA_RESERVADA", "elif"):
            orelse = [self.if_statement()]
        elif self.match("PALAVRA_RESERVADA", "else"):
            self.expect("DELIMITADOR", ":")
            orelse = self.block()
        return {
            "type": "IfStatement",
            "condition": condition,
            "body": body,
            "orelse": orelse,
            "line": token["linha"],
        }

    def def_statement(self):
        token = self.advance()
        name = self.expect("IDENTIFICADOR", what="o nome da função")["lexema"]
        self.expect("DELIMITADOR", "(")
        params = []
        if not self.check("DELIMITADOR", ")"):
            params.append(self.expect("IDENTIFICADOR", what="o nome de um parâmetro")["lexema"])
            while self.match("DELIMITADOR", ","):
                params.append(
                    self.expect("IDENTIFICADOR", what="o nome de um parâmetro")["lexema"]
                )
        self.expect("DELIMITADOR", ")")
        self.expect("DELIMITADOR", ":")
        body = self.block()
        return {
            "type": "FunctionDef",
            "name": name,
            "params": params,
            "body": body,
            "line": token["linha"],
        }

    def return_statement(self):
        token = self.advance()
        value = None if self.check("NOVA_LINHA") else self.expression()
        self.expect_newline()
        return {"type": "ReturnStatement", "value": value, "line": token["linha"]}

    def assignment(self):
        name = self.advance()
        self.advance()  # '='
        value = self.expression()
        self.expect_newline()
        return {
            "type": "Assignment",
            "variable": name["lexema"],
            "value": value,
            "line": name["linha"],
        }

    # ---------- expressões ----------
    def _binary(self, operand, operators):
        left = operand()
        while self.check("OPERADOR") and self.peek()["lexema"] in operators:
            op = self.advance()["lexema"]
            right = operand()
            left = {"type": "BinaryExpression", "operator": op, "left": left, "right": right}
        return left

    def expression(self):
        return self._binary(self.additive, COMPARISON_OPS)

    def additive(self):
        return self._binary(self.term, {"+", "-"})

    def term(self):
        return self._binary(self.unary, {"*", "/"})

    def unary(self):
        if self.check("OPERADOR", "-"):
            self.advance()
            return {"type": "UnaryExpression", "operator": "-", "operand": self.unary()}
        return self.primary()

    def primary(self):
        token = self.peek()
        tipo = token["tipo"]

        if tipo == "LITERAL_INTEIRO":
            self.advance()
            return {"type": "Literal", "kind": "number", "value": int(token["lexema"])}
        if tipo == "LITERAL_REAL":
            self.advance()
            return {"type": "Literal", "kind": "number", "value": float(token["lexema"])}
        if tipo == "LITERAL_STRING":
            self.advance()
            return {"type": "Literal", "kind": "string", "value": token["lexema"][1:-1]}
        if tipo == "IDENTIFICADOR":
            self.advance()
            if self.match("DELIMITADOR", "("):
                args = []
                if not self.check("DELIMITADOR", ")"):
                    args.append(self.expression())
                    while self.match("DELIMITADOR", ","):
                        args.append(self.expression())
                self.expect("DELIMITADOR", ")")
                return {"type": "CallExpression", "callee": token["lexema"], "arguments": args}
            return {"type": "Identifier", "name": token["lexema"]}
        if self.match("DELIMITADOR", "("):
            expr = self.expression()
            self.expect("DELIMITADOR", ")")
            return expr
        if tipo == "PALAVRA_RESERVADA":
            raise self.error(
                f"A palavra reservada '{token['lexema']}' não pode ser usada aqui "
                "ou ainda não é suportada pela prévia do analisador sintático.",
                token,
            )

        raise self.error(
            f"Esperada uma expressão, mas encontrou {self.describe(token)}.", token
        )