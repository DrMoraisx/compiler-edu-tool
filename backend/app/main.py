from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

# 1. Instanciação inicial da aplicação FastAPI (essencial vir primeiro)
app = FastAPI(title="Compiler Edu Tool API - Lexical Analyzer")

# 2. Configuração de CORS para o React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

# 3. Definição dos tipos de tokens para o nosso subconjunto de Mini-Python
TOKEN_TYPES = [
    ("COMMENT", r"#.*"),
    ("KEYWORD", r"\b(if|else|while|def|return|print)\b"),
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("NUMBER", r"\b\d+(\.\d+)?\b"),
    ("OPERATOR", r"==|!=|<=|>=|[+\-*/=<>]"),
    ("DELIMITER", r"[(),:\[\]{}]"),
    ("WHITESPACE", r"\s+"),
    ("UNKNOWN", r"."),  # caractere inválido
]

@app.get("/")
def read_root():
    return {"message": "Hello, World! Backend do Compilador Educacional online."}

@app.post("/api/lexical")
def lexical_analysis(req: CodeRequest):
    code = req.code
    tokens = []
    errors = []
    
    # Construção da regex unificada
    master_pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_TYPES)
    
    line_num = 1
    column = 1
    
    for match in re.finditer(master_pattern, code):
        kind = match.lastgroup
        value = match.group(kind)
        
        if kind == "WHITESPACE":
            line_num += value.count("\n")
            if "\n" in value:
                column = len(value) - value.rfind("\n")
            else:
                column += len(value)
            continue
            
        if kind == "COMMENT":
            tokens.append({"type": kind, "value": value, "line": line_num, "column": column})
        elif kind == "UNKNOWN":
            errors.append({"error": f"Caractere desconhecido '{value}'", "line": line_num, "column": column})
        else:
            tokens.append({"type": kind, "value": value, "line": line_num, "column": column})
            
        column += len(value)
            
    return {
        "tokens": tokens,
        "errors": errors
    }