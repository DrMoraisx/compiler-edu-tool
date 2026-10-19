from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from app.parser import Parser

app = FastAPI(title="Compiler Edu Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

TOKEN_TYPES = [
    ("COMMENT", r"#.*"),
    ("KEYWORD", r"\b(if|else|while|def|return|print)\b"),
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("NUMBER", r"\b\d+(\.\d+)?\b"),
    ("OPERATOR", r"==|!=|<=|>=|[+\-*/=<>]"),
    ("DELIMITER", r"[(),:\[\]{}]"),
    ("WHITESPACE", r"\s+"),
    ("UNKNOWN", r"."),
]

@app.post("/api/lexical")
def lexical_analysis(req: CodeRequest):
    code = req.code
    tokens = []
    errors = []
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
            
    return {"tokens": tokens, "errors": errors}

@app.post("/api/parse")
def parse_code(req: CodeRequest):
    # Primeiro executa a análise léxica para obter os tokens limpos (sem whitespace)
    lex_res = lexical_analysis(req)
    if lex_res["errors"]:
        raise HTTPException(status_code=400, detail="Existem erros léxicos que impedem a análise sintática.")
    
    tokens = lex_res["tokens"]
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        return {"ast": ast, "error": None}
    except Exception as e:
        return {"ast": None, "error": str(e)}