
class ErroSintatico(Exception):
    def __init__(self, mensagem, token=None, esperado=None):
        self.mensagem = mensagem
        self.token = token
        self.esperado = esperado
        super().__init__(mensagem)


class Parser:
    """
    Parser descendente recursivo para Mini-Python.

    Reconhece:
    - Atribuições simples
    - Comando print
    - Condicionais if/else
    - Blocos indentados
    - Expressões aritméticas
    - Expressões relacionais
    - Literais inteiros, reais e textuais
    - Identificadores
    - Expressões entre parênteses
    - Negação numérica unária

    Gera uma Árvore Sintática Abstrata (AST).
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0

    def atual(self):
        if self.posicao < len(self.tokens):
            return self.tokens[self.posicao]

        return {
            "tipo": "EOF",
            "lexema": "<EOF>",
            "linha": 1,
            "coluna": 1
        }

    def avancar(self):
        token = self.atual()

        if token["tipo"] != "EOF":
            self.posicao += 1

        return token

    def verificar(self, tipo=None, lexema=None):
        token = self.atual()

        if tipo is not None and token["tipo"] != tipo:
            return False

        if lexema is not None and token["lexema"] != lexema:
            return False

        return True

    def consumir(self, tipo=None, lexema=None):
        token = self.atual()

        if not self.verificar(tipo, lexema):
            esperado = (
                lexema
                if lexema is not None
                else tipo
            )

            encontrado = token["lexema"]

            raise ErroSintatico(
                f"Esperado '{esperado}', mas encontrado '{encontrado}'.",
                token,
                esperado
            )

        return self.avancar()

    def ignorar_quebras(self):
        while self.verificar("NOVA_LINHA"):
            self.avancar()

    def criar_no(self, tipo, token=None, **atributos):
        no = {
            "tipo": tipo,
            **atributos
        }

        if token:
            no["posicao"] = {
                "linha": token["linha"],
                "coluna": token["coluna"]
            }

        return no

    # =====================================================
    # ANÁLISE PRINCIPAL
    # =====================================================

    def analisar(self):
        corpo = []
        erros = []

        self.ignorar_quebras()

        while not self.verificar("EOF"):

            if self.verificar("DEDENT"):
                self.avancar()
                continue

            try:
                declaracao = self.declaracao()
                corpo.append(declaracao)

                self.ignorar_quebras()

            except ErroSintatico as erro:
                token = erro.token or self.atual()

                erros.append({
                    "mensagem": erro.mensagem,
                    "linha": token["linha"],
                    "coluna": token["coluna"],
                    "encontrado": token["lexema"],
                    "esperado": erro.esperado
                })

                # Recuperação por sincronização no final da linha.
                while (
                    not self.verificar("NOVA_LINHA")
                    and not self.verificar("EOF")
                    and not self.verificar("DEDENT")
                ):
                    self.avancar()

                self.ignorar_quebras()

        return {
            "ast": self.criar_no(
                "Programa",
                corpo=corpo
            ),
            "erros": erros
        }

    # =====================================================
    # DECLARAÇÕES E COMANDOS
    # =====================================================

    def declaracao(self):
        token = self.atual()

        if self.verificar(
            "PALAVRA_RESERVADA",
            "print"
        ):
            return self.declaracao_print()

        if self.verificar(
            "PALAVRA_RESERVADA",
            "if"
        ):
            return self.declaracao_if()

        if self.verificar("IDENTIFICADOR"):
            return self.atribuicao()

        raise ErroSintatico(
            f"Comando não reconhecido: '{token['lexema']}'.",
            token,
            "print, if ou identificador"
        )

    def declaracao_print(self):
        inicio = self.consumir(
            "PALAVRA_RESERVADA",
            "print"
        )

        self.consumir(
            "DELIMITADOR",
            "("
        )

        expressao = self.expressao()

        self.consumir(
            "DELIMITADOR",
            ")"
        )

        return self.criar_no(
            "Print",
            inicio,
            expressao=expressao
        )

    def atribuicao(self):
        nome = self.consumir("IDENTIFICADOR")

        self.consumir(
            "OPERADOR",
            "="
        )

        valor = self.expressao()

        return self.criar_no(
            "Atribuicao",
            nome,
            identificador=nome["lexema"],
            valor=valor
        )

    # =====================================================
    # CONDICIONAIS E BLOCOS
    # =====================================================

    def declaracao_if(self):
        inicio = self.consumir(
            "PALAVRA_RESERVADA",
            "if"
        )

        condicao = self.expressao()

        self.consumir(
            "DELIMITADOR",
            ":"
        )

        self.ignorar_quebras()

        corpo_if = self.bloco_indentado()

        corpo_else = []

        if self.verificar(
            "PALAVRA_RESERVADA",
            "else"
        ):
            self.avancar()

            self.consumir(
                "DELIMITADOR",
                ":"
            )

            self.ignorar_quebras()

            corpo_else = self.bloco_indentado()

        return self.criar_no(
            "Condicional",
            inicio,
            condicao=condicao,
            corpo_if=corpo_if,
            corpo_else=corpo_else
        )

    def bloco_indentado(self):
        comandos = []

        self.consumir("INDENT")

        self.ignorar_quebras()

        while (
            not self.verificar("DEDENT")
            and not self.verificar("EOF")
        ):
            comandos.append(
                self.declaracao()
            )

            self.ignorar_quebras()

        self.consumir("DEDENT")

        return comandos

    # =====================================================
    # EXPRESSÕES
    #
    # Precedência:
    # 1. Valores e parênteses
    # 2. Negação unária
    # 3. Multiplicação, divisão e módulo
    # 4. Soma e subtração
    # 5. Comparações
    #
    # Operações binárias são associadas à esquerda.
    # =====================================================

    def expressao(self):
        esquerda = self.soma()

        while (
            self.verificar("OPERADOR")
            and self.atual()["lexema"] in (
                "==",
                "!=",
                "<",
                ">",
                "<=",
                ">="
            )
        ):
            operador = self.avancar()

            direita = self.soma()

            esquerda = self.criar_no(
                "ExpressaoBinaria",
                operador,
                operador=operador["lexema"],
                esquerda=esquerda,
                direita=direita
            )

        return esquerda

    def soma(self):
        esquerda = self.multiplicacao()

        while (
            self.verificar("OPERADOR")
            and self.atual()["lexema"] in (
                "+",
                "-"
            )
        ):
            operador = self.avancar()

            direita = self.multiplicacao()

            esquerda = self.criar_no(
                "ExpressaoBinaria",
                operador,
                operador=operador["lexema"],
                esquerda=esquerda,
                direita=direita
            )

        return esquerda

    def multiplicacao(self):
        esquerda = self.fator()

        while (
            self.verificar("OPERADOR")
            and self.atual()["lexema"] in (
                "*",
                "/",
                "%"
            )
        ):
            operador = self.avancar()

            direita = self.fator()

            esquerda = self.criar_no(
                "ExpressaoBinaria",
                operador,
                operador=operador["lexema"],
                esquerda=esquerda,
                direita=direita
            )

        return esquerda

    # =====================================================
    # FATORES, IDENTIFICADORES E LITERAIS
    # =====================================================

    def fator(self):
        token = self.atual()

        # Literais inteiros e reais.
        if token["tipo"] in (
            "LITERAL_INTEIRO",
            "LITERAL_REAL",
            "LITERAL_NUMERO"
        ):
            self.avancar()

            return self.criar_no(
                "Literal",
                token,
                valor=token["lexema"],
                tipo_valor="numero"
            )

        # Literais textuais.
        if token["tipo"] in (
            "LITERAL_STRING",
            "LITERAL_TEXTO"
        ):
            self.avancar()

            return self.criar_no(
                "Literal",
                token,
                valor=token["lexema"],
                tipo_valor="texto"
            )

        # Identificadores.
        if self.verificar("IDENTIFICADOR"):
            self.avancar()

            return self.criar_no(
                "Identificador",
                token,
                nome=token["lexema"]
            )

        # Negação numérica unária.
        if self.verificar(
            "OPERADOR",
            "-"
        ):
            operador = self.avancar()

            valor = self.fator()

            return self.criar_no(
                "ExpressaoUnaria",
                operador,
                operador="-",
                valor=valor
            )

        # Expressões entre parênteses.
        if self.verificar(
            "DELIMITADOR",
            "("
        ):
            self.avancar()

            expressao = self.expressao()

            self.consumir(
                "DELIMITADOR",
                ")"
            )

            return expressao

        raise ErroSintatico(
            (
                "Expressão incompleta ou inválida "
                f"perto de '{token['lexema']}'."
            ),
            token,
            "número, texto, identificador ou '('"
        )
