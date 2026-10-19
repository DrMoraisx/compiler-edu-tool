class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type):
        token = self.current_token()
        if token and token["type"] == token_type:
            self.pos += 1
            return token
        else:
            current_type = token["type"] if token else "EOF"
            current_val = token["value"] if token else "EOF"
            raise SyntaxError(f"Esperado token do tipo '{token_type}', mas encontrou '{current_val}' (tipo: {current_type})")

    def parse(self):
        statements = []
        while self.current_token() is not None:
            if self.current_token()["type"] == "WHITESPACE" or self.current_token()["type"] == "COMMENT":
                self.pos += 1
                continue
            statements.append(self.statement())
        return {"type": "Program", "body": statements}

    def statement(self):
        token = self.current_token()
        if not token:
            return None

        # Print statement
        if token["type"] == "KEYWORD" and token["value"] == "print":
            self.eat("KEYWORD")
            self.eat("DELIMITER") # (
            expr = self.expression()
            self.eat("DELIMITER") # )
            return {"type": "PrintStatement", "expression": expr}

        # If statement
        elif token["type"] == "KEYWORD" and token["value"] == "if":
            self.eat("KEYWORD")
            condition = self.expression()
            self.eat("DELIMITER") # :
            body = []
            while self.current_token() and self.current_token()["value"] != "else": # Simplificação para o bloco
                statements_in_block = self.statement()
                if statements_in_block:
                    body.append(statements_in_block)
            return {"type": "IfStatement", "condition": condition, "body": body}

        # Def (Function definition)
        elif token["type"] == "KEYWORD" and token["value"] == "def":
            self.eat("KEYWORD")
            func_name = self.eat("IDENTIFIER")["value"]
            self.eat("DELIMITER") # (
            params = []
            if self.current_token() and self.current_token()["type"] == "IDENTIFIER":
                params.append(self.eat("IDENTIFIER")["value"])
                while self.current_token() and self.current_token()["value"] == ",":
                    self.eat("DELIMITER")
                    params.append(self.eat("IDENTIFIER")["value"])
            self.eat("DELIMITER") # )
            self.eat("DELIMITER") # :
            return {"type": "FunctionDef", "name": func_name, "params": params}

        # Atribuição ou Expressão com Identificador
        elif token["type"] == "IDENTIFIER":
            var_name = self.eat("IDENTIFIER")["value"]
            if self.current_token() and self.current_token()["value"] == "=":
                self.eat("OPERATOR")
                expr = self.expression()
                return {"type": "Assignment", "variable": var_name, "value": expr}
            else:
                return {"type": "IdentifierExpression", "value": var_name}

        else:
            # Consumir tokens avulsos para evitar loop infinito em caso de erro sintático simples
            self.pos += 1
            return {"type": "Unknown", "value": token["value"]}

    def expression(self):
        left = self.term()
        while self.current_token() and self.current_token()["value"] in ["+", "-", "==", "!=", "<", ">", "<=", ">="]:
            op = self.current_token()["value"]
            self.pos += 1
            right = self.term()
            left = {"type": "BinaryExpression", "operator": op, "left": left, "right": right}
        return left

    def term(self):
        token = self.current_token()
        if token and token["type"] == "NUMBER":
            self.pos += 1
            return {"type": "Literal", "value": token["value"]}
        elif token and token["type"] == "IDENTIFIER":
            self.pos += 1
            return {"type": "Identifier", "value": token["value"]}
        elif token and token["value"] == "(":
            self.eat("DELIMITER")
            expr = self.expression()
            self.eat("DELIMITER")
            return expr
        else:
            if token:
                self.pos += 1
                return {"type": "Literal", "value": token["value"]}
            return {"type": "Literal", "value": ""}