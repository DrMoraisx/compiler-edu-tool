
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator

from app.lexer import analisar_lexico
from app.parser import Parser


app = FastAPI(
    title="Mini-Python Compiler Educational Tool",
    description=(
        "Software educacional para análise léxica, "
        "análise sintática e geração de AST."
    ),
    version="4.2.0"
)


# =========================================================
# CONFIGURAÇÃO CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# MODELO DE ENTRADA
# =========================================================

class CodeRequest(BaseModel):
    code: str | None = None
    codigo: str | None = None

    @model_validator(mode="after")
    def validar_codigo(self):
        if self.code is None and self.codigo is None:
            raise ValueError(
                "Informe o campo 'code' ou 'codigo'."
            )

        return self

    def obter_codigo(self):
        if self.code is not None:
            return self.code

        return self.codigo


# =========================================================
# ROTAS DE SAÚDE E INFORMAÇÕES
# =========================================================

@app.get("/")
def read_root():
    return {
        "message": "Mini-Python Compiler Backend",
        "status": "active",
        "version": "4.2.0",
        "features": [
            "analise_lexica",
            "analise_sintatica",
            "ast"
        ]
    }


@app.get("/api/health")
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend funcionando corretamente",
        "version": "4.2.0"
    }


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def filtrar_tokens_visiveis(tokens):
    """
    Mantém o formato de tokens da Etapa 3.

    Os tokens estruturais continuam disponíveis em
    tokens_parser e são exibidos pela interface atual.
    """

    estruturais = {
        "NOVA_LINHA",
        "INDENT",
        "DEDENT",
        "INDENTACAO",
        "DESINDENTACAO",
        "EOF"
    }

    return [
        token
        for token in tokens
        if token["tipo"] not in estruturais
    ]


def formatar_erros_sintaticos(erros):
    """
    Padroniza os erros sintáticos para o contrato da API.
    """

    formatados = []

    for erro in erros:
        formatados.append({
            "tipo": "ERRO_SINTATICO",
            "mensagem": erro.get(
                "mensagem",
                "Erro na estrutura do código."
            ),
            "linha": erro.get("linha", 1),
            "coluna": erro.get("coluna", 1),
            "encontrado": erro.get("encontrado"),
            "esperado": erro.get("esperado")
        })

    return formatados


# =========================================================
# ANÁLISE LÉXICA E SINTÁTICA
# =========================================================

@app.post("/api/parse")
@app.post("/api/analyze")
def parse_code(request: CodeRequest):

    codigo = request.obter_codigo()

    if codigo is None or not codigo.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "Informe um código-fonte antes de "
                "solicitar a análise."
            )
        )

    # -----------------------------------------------------
    # 1. ANÁLISE LÉXICA
    # -----------------------------------------------------

    resultado_lexico = analisar_lexico(codigo)

    tokens_completos = resultado_lexico["tokens"]
    erros_lexicos = resultado_lexico["erros"]

    # Lista compatível com o formato visual da Etapa 3.
    tokens_legados = filtrar_tokens_visiveis(
        tokens_completos
    )

    # -----------------------------------------------------
    # 2. ERROS LÉXICOS
    # -----------------------------------------------------

    if erros_lexicos:

        return {
            "message": (
                "A análise sintática não foi executada "
                "porque existem erros léxicos."
            ),

            # Compatibilidade com versões anteriores.
            "recebido": True,
            "success": False,
            "sucesso": False,
            "tokens": tokens_legados,
            "erros": erros_lexicos,

            # Sequência completa produzida pelo scanner.
            "tokens_parser": tokens_completos,

            # Resultado léxico.
            "sucesso_lexico": False,
            "erros_lexicos": erros_lexicos,

            # Resultado sintático.
            "sucesso_sintatico": False,
            "sintatico_executado": False,
            "ast": None,
            "erros_sintaticos": [],

            # Contrato agrupado.
            "lexico": {
                "sucesso": False,
                "tokens": tokens_completos,
                "erros": erros_lexicos
            },
            "sintatico": {
                "executado": False,
                "sucesso": False,
                "ast": None,
                "erros": []
            }
        }

    # -----------------------------------------------------
    # 3. ANÁLISE SINTÁTICA
    # -----------------------------------------------------

    # O parser recebe exatamente a sequência completa
    # produzida pelo lexer, inclusive tokens estruturais.
    parser = Parser(tokens_completos)

    resultado_sintatico = parser.analisar()

    erros_sintaticos = formatar_erros_sintaticos(
        resultado_sintatico["erros"]
    )

    sucesso_sintatico = len(erros_sintaticos) == 0

    # A AST somente é disponibilizada quando a análise
    # sintática termina sem erros.
    ast = (
        resultado_sintatico["ast"]
        if sucesso_sintatico
        else None
    )

    # -----------------------------------------------------
    # 4. CONSOLIDAÇÃO
    # -----------------------------------------------------

    sucesso = sucesso_sintatico

    if sucesso:
        mensagem = (
            "Análise léxica e sintática concluída com sucesso."
        )
    else:
        mensagem = (
            "A análise léxica foi concluída, "
            "mas foram encontrados erros sintáticos."
        )

    # -----------------------------------------------------
    # 5. RESPOSTA
    # -----------------------------------------------------

    return {
        "message": mensagem,

        # Compatibilidade com a Etapa 3.
        "recebido": True,
        "success": sucesso,
        "sucesso": sucesso,
        "tokens": tokens_legados,
        "erros": erros_sintaticos,

        # Sequência completa consumida pelo parser.
        "tokens_parser": tokens_completos,

        # Campos detalhados da Etapa 4.
        "sucesso_lexico": True,
        "sucesso_sintatico": sucesso_sintatico,
        "sintatico_executado": True,
        "erros_lexicos": [],
        "ast": ast,
        "erros_sintaticos": erros_sintaticos,

        # Contrato agrupado.
        "lexico": {
            "sucesso": True,
            "tokens": tokens_completos,
            "erros": []
        },
        "sintatico": {
            "executado": True,
            "sucesso": sucesso_sintatico,
            "ast": ast,
            "erros": erros_sintaticos
        }
    }
