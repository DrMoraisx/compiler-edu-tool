
import re
from dataclasses import dataclass


# =========================================================
# DEFINIÇÃO DOS TOKENS
# =========================================================

PALAVRAS_RESERVADAS = {
    "if",
    "else",
    "print",
}

OPERADORES_SIMPLES = {
    "+", "-", "*", "/", "%", "=", "<", ">",
}

OPERADORES_DUPLOS = {
    "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=",
}

OPERADORES = OPERADORES_SIMPLES | OPERADORES_DUPLOS

DELIMITADORES = {
    "(", ")", ":", ",",
}

ESTRUTURAIS = {
    "NOVA_LINHA",
    "INDENTACAO",
    "DESINDENTACAO",
    "INDENT",
    "DEDENT",
    "EOF",
}


class CompilerError(Exception):
    """Erro léxico apresentado de forma estruturada."""

    def __init__(self, mensagem, fase="léxico", linha=1, coluna=1,
                 lexema="", tipo="ERRO_LEXICO"):
        self.mensagem = mensagem
        self.fase = fase
        self.linha = linha
        self.coluna = coluna
        self.lexema = lexema
        self.tipo = tipo
        super().__init__(mensagem)

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "lexema": self.lexema,
            "linha": self.linha,
            "coluna": self.coluna,
            "mensagem": self.mensagem,
        }


@dataclass
class Token:
    tipo: str
    lexema: str
    linha: int
    coluna: int

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "lexema": self.lexema,
            "linha": self.linha,
            "coluna": self.coluna,
        }


# =========================================================
# ANALISADOR LÉXICO
# =========================================================

class Lexer:
    PALAVRAS_RESERVADAS = PALAVRAS_RESERVADAS
    OPERADORES = OPERADORES
    DELIMITADORES = DELIMITADORES

    def __init__(self, codigo):
        self.codigo = codigo or ""
        self.tokens = []
        self.erros = []
        self.indentacoes = [0]

    def adicionar_token(self, tipo, lexema, linha, coluna):
        self.tokens.append({
            "tipo": tipo,
            "lexema": lexema,
            "linha": linha,
            "coluna": coluna,
        })

    def adicionar_erro(self, lexema, linha, coluna, mensagem):
        self.erros.append({
            "tipo": "ERRO_LEXICO",
            "lexema": lexema,
            "linha": linha,
            "coluna": coluna,
            "mensagem": mensagem,
        })

    @staticmethod
    def identificador_inicio(caractere):
        return caractere == "_" or caractere.isalpha()

    @staticmethod
    def identificador_parte(caractere):
        return caractere == "_" or caractere.isalnum()

    def analisar_linha(self, conteudo, numero_linha):
        # Expande tabulações para quatro espaços.
        conteudo = conteudo.expandtabs(4)

        if not conteudo.strip():
            return

        sem_espacos = conteudo.lstrip(" ")
        if sem_espacos.startswith("#"):
            return

        espacos = len(conteudo) - len(sem_espacos)

        if espacos > self.indentacoes[-1]:
            self.indentacoes.append(espacos)
            self.adicionar_token(
                "INDENTACAO", "", numero_linha, 1
            )

        elif espacos < self.indentacoes[-1]:
            while (
                len(self.indentacoes) > 1
                and espacos < self.indentacoes[-1]
            ):
                self.indentacoes.pop()
                self.adicionar_token(
                    "DESINDENTACAO", "", numero_linha, 1
                )

            if espacos != self.indentacoes[-1]:
                self.adicionar_erro(
                    "",
                    numero_linha,
                    1,
                    "Indentação inconsistente no subconjunto suportado.",
                )

        texto = conteudo[espacos:]
        posicao = 0

        while posicao < len(texto):
            caractere = texto[posicao]
            coluna = espacos + posicao + 1

            if caractere.isspace():
                posicao += 1
                continue

            # Comentário fora de strings.
            if caractere == "#":
                break

            # Strings.
            if caractere in ('"', "'"):
                aspas = caractere
                inicio = posicao
                posicao += 1
                fechou = False

                while posicao < len(texto):
                    atual = texto[posicao]

                    if atual == "\\":
                        posicao += 2
                        continue

                    if atual == aspas:
                        posicao += 1
                        fechou = True
                        break

                    posicao += 1

                lexema = texto[inicio:min(posicao, len(texto))]

                if fechou:
                    self.adicionar_token(
                        "LITERAL_STRING",
                        lexema,
                        numero_linha,
                        coluna,
                    )
                else:
                    self.adicionar_erro(
                        lexema,
                        numero_linha,
                        coluna,
                        "String não terminada no subconjunto suportado.",
                    )

                continue

            # Números inteiros e reais.
            if caractere.isdigit():
                inicio = posicao

                while (
                    posicao < len(texto)
                    and texto[posicao].isdigit()
                ):
                    posicao += 1

                tipo_numero = "LITERAL_INTEIRO"

                if (
                    posicao + 1 < len(texto)
                    and texto[posicao] == "."
                    and texto[posicao + 1].isdigit()
                ):
                    tipo_numero = "LITERAL_REAL"
                    posicao += 1

                    while (
                        posicao < len(texto)
                        and texto[posicao].isdigit()
                    ):
                        posicao += 1

                # Número seguido diretamente por identificador.
                if (
                    posicao < len(texto)
                    and self.identificador_inicio(texto[posicao])
                ):
                    while (
                        posicao < len(texto)
                        and self.identificador_parte(texto[posicao])
                    ):
                        posicao += 1

                    lexema = texto[inicio:posicao]
                    self.adicionar_erro(
                        lexema,
                        numero_linha,
                        coluna,
                        "Número malformado no subconjunto suportado.",
                    )
                    continue

                lexema = texto[inicio:posicao]
                self.adicionar_token(
                    tipo_numero,
                    lexema,
                    numero_linha,
                    coluna,
                )
                continue

            # Identificadores e palavras reservadas.
            if self.identificador_inicio(caractere):
                inicio = posicao
                posicao += 1

                while (
                    posicao < len(texto)
                    and self.identificador_parte(texto[posicao])
                ):
                    posicao += 1

                lexema = texto[inicio:posicao]

                tipo = (
                    "PALAVRA_RESERVADA"
                    if lexema in PALAVRAS_RESERVADAS
                    else "IDENTIFICADOR"
                )

                self.adicionar_token(
                    tipo,
                    lexema,
                    numero_linha,
                    coluna,
                )
                continue

            # Operadores: tenta reconhecer primeiro os de dois caracteres.
            operador_encontrado = None

            if posicao + 1 < len(texto):
                candidato = texto[posicao:posicao + 2]
                if candidato in OPERADORES_DUPLOS:
                    operador_encontrado = candidato

            if operador_encontrado:
                self.adicionar_token(
                    "OPERADOR",
                    operador_encontrado,
                    numero_linha,
                    coluna,
                )
                posicao += 2
                continue

            if caractere in OPERADORES_SIMPLES:
                self.adicionar_token(
                    "OPERADOR",
                    caractere,
                    numero_linha,
                    coluna,
                )
                posicao += 1
                continue

            # Delimitadores.
            if caractere in DELIMITADORES:
                self.adicionar_token(
                    "DELIMITADOR",
                    caractere,
                    numero_linha,
                    coluna,
                )
                posicao += 1
                continue

            # Exclamação isolada.
            if caractere == "!":
                self.adicionar_erro(
                    caractere,
                    numero_linha,
                    coluna,
                    "Operador inválido. Você quis utilizar '!='?",
                )
                posicao += 1
                continue

            # Qualquer outro caractere.
            self.adicionar_erro(
                caractere,
                numero_linha,
                coluna,
                (
                    f"Caractere '{caractere}' não pertence ao "
                    "subconjunto suportado da linguagem."
                ),
            )
            posicao += 1

        self.adicionar_token(
            "NOVA_LINHA",
            "\n",
            numero_linha,
            len(conteudo) + 1,
        )

    def analisar(self):
        linhas = self.codigo.splitlines()

        for numero_linha, conteudo in enumerate(linhas, start=1):
            self.analisar_linha(conteudo, numero_linha)

        # Fecha todos os blocos abertos.
        ultima_linha = max(len(linhas), 1)

        while len(self.indentacoes) > 1:
            self.indentacoes.pop()
            self.adicionar_token(
                "DESINDENTACAO",
                "",
                ultima_linha,
                1,
            )

        return self.tokens, self.erros


# =========================================================
# INTERFACES COMPATÍVEIS COM A ETAPA 3
# =========================================================

def scan(codigo):
    """Retorna (tokens, erros), sem lançar exceção."""
    lexer = Lexer(codigo)
    return lexer.analisar()


def tokenize(codigo):
    """Retorna tokens ou lança CompilerError no primeiro erro."""
    tokens, erros = scan(codigo)

    if erros:
        erro = erros[0]
        raise CompilerError(
            mensagem=erro["mensagem"],
            fase="léxico",
            linha=erro["linha"],
            coluna=erro["coluna"],
            lexema=erro["lexema"],
        )

    return tokens


def analisar_lexico(codigo):
    """Interface utilizada pela API e pelo Parser."""
    tokens, erros = scan(codigo)

    # Mantém os nomes estruturais esperados pelo Parser atual.
    tokens_api = []

    for token in tokens:
        convertido = dict(token)

        if convertido["tipo"] == "INDENTACAO":
            convertido["tipo"] = "INDENT"

        elif convertido["tipo"] == "DESINDENTACAO":
            convertido["tipo"] = "DEDENT"

        tokens_api.append(convertido)

    return {
        "tokens": tokens_api,
        "erros": erros,
    }
