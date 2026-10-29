
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from .lexer import tokenize, CompilerError
from .parser import Parser

from .scanner import scan

app = FastAPI(
    title="Compiler Edu Tool - Mini-Python",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)






class CodeRequest(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

    code: str = Field(
        ...,
        alias="codigo",
        description="Código-fonte Mini-Python"
    )




@app.get("/")
def read_root():
    return {
        "message": "Mini-Python Compiler Backend is running",
        "status": "active"
    }

@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}




@app.post("/api/parse")
@app.post("/api/analyze")
def analyze_code(request: CodeRequest):
    code = request.code

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Informe um código-fonte antes de solicitar a análise."
        )

    if not code.strip():
        raise HTTPException(
            status_code=400,
            detail="O código-fonte não pode ser composto apenas por espaços em branco."
        )

    # Mantém a verificação léxica usada atualmente pelo projeto.
    tokens, errors = scan(code)

    # Preserva a resposta HTTP 200 para códigos que contenham
    # erros léxicos, informando os erros no corpo da resposta.
    if errors:
        return {
            "mensagem": "Análise concluída com erros léxicos.",
            "recebido": True,
            "sucesso": False,
            "success": False,
            "tokens": tokens,
            "erros": errors,
            "ast": None,
            "resumo": {
                "total_tokens": len(tokens),
                "total_erros": len(errors)
            }
        }

    try:
        # O lexer correto produz os tokens estruturais do parser.
        parser_tokens = tokenize(code)
        ast = Parser(parser_tokens).parse()

    except CompilerError as exc:
        raise HTTPException(
            status_code=400,
            detail=exc.mensagem
        )

    return {
        "mensagem": "Análise concluída com sucesso.",
        "recebido": True,
        "sucesso": True,
        "success": True,
        "tokens": [
            token for token in parser_tokens
            if token["tipo"] != "NOVA_LINHA"
        ],
        "erros": [],
        "ast": ast,
        "resumo": {
            "total_tokens": len(parser_tokens),
            "total_erros": 0
        }
    }



