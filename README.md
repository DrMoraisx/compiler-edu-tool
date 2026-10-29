
# Compiler Edu Tool — Analisador Educacional de Mini-Python

## 1. Apresentação

O Compiler Edu Tool é um software educacional desenvolvido para
demonstrar conceitos de compiladores por meio de uma aplicação web.

O projeto está organizado em etapas progressivas:
- Etapa 1: estrutura inicial, linguagem escolhida e Docker.
- Etapa 2: interface web e comunicação entre frontend e backend.
- Etapa 3: análise léxica do código-fonte.

## 2. Linguagem escolhida

A linguagem escolhida para análise é um subconjunto didático de
Python, denominado Mini-Python.

Python foi escolhido por possuir sintaxe legível e permitir
demonstrar conceitos de análise léxica com exemplos simples.

O scanner é implementado em Python com FastAPI. A interface é
desenvolvida em React.

## 3. Escopo inicial

O analisador léxico reconhece:

- Palavras reservadas: if, else, while, for, in, def, return,
  print, and, or, not, True, False e None.
- Identificadores: nomes iniciados por letras ou sublinhado.
- Literais inteiros: exemplos 0, 10 e 2048.
- Literais reais: exemplos 3.14 e 0.5.
- Strings com aspas simples ou duplas.
- Operadores aritméticos, relacionais e de atribuição.
- Delimitadores: parênteses, colchetes, chaves, dois-pontos,
  vírgulas e ponto.
- Comentários iniciados pelo caractere #.
- Erros léxicos, com indicação de linha e coluna.

Espaços em branco e comentários são ignorados.

Esta versão não executa o código analisado, não valida toda a
gramática de Python e ainda não implementa análise sintática,
indentação ou análise semântica.

## 4. Tecnologias utilizadas

- Python 3.11.
- FastAPI e Uvicorn.
- React 18.
- Docker.
- Docker Compose.
- Pytest.
- Jest e React Testing Library.

## 5. Estrutura do projeto

```text
compiler-edu-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── scanner.py
│   ├── tests/
│   │   ├── test_main.py
│   │   └── test_scanner.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/index.html
│   ├── src/App.js
│   ├── src/App.css
│   ├── src/App.test.js
│   ├── src/index.js
│   ├── package.json
│   └── Dockerfile
├── docs/
│   └── TESTES.md
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 6. Pré-requisitos

- Docker Desktop ou Docker Engine.
- Docker Compose v2, disponível pelo comando docker compose.
- Conexão com a internet durante a primeira construção das imagens.

Para executar os testes localmente, também são necessários Python
3.11 ou superior e Node.js 18 ou superior.

## 7. Executar com Docker

Na pasta raiz do projeto, execute:

```bash
docker compose up --build -d
```

Verifique os serviços:

```bash
docker compose ps
```

Acompanhe os logs:

```bash
docker compose logs -f
```

A interface estará disponível em:

http://localhost:3000

A API estará disponível em:

http://localhost:8000

Documentação interativa da API:

http://localhost:8000/docs

Verificação de saúde:

http://localhost:8000/api/health

Para encerrar:

```bash
docker compose down
```

## 8. API de análise

O endpoint principal é:

POST /api/parse

Também está disponível:

POST /api/analyze

Exemplo de requisição:

```json
{
  "code": "numero = 10"
}
```

A resposta contém:
- mensagem: resultado geral da análise.
- recebido: confirmação de recebimento.
- sucesso: indica se foram encontrados erros léxicos.
- tokens: tokens reconhecidos.
- erros: erros léxicos encontrados.
- resumo: quantidade de tokens e erros.
- observacao: limitações da análise atual.

Cada token possui tipo, lexema, linha e coluna.

Entradas vazias retornam HTTP 400. Requisições com corpo
incompatível retornam HTTP 422.

## 9. Testes do backend

Execute:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
```

## 10. Testes do frontend

Execute:

```bash
cd frontend
npm install
npm test
```

## 11. Validação do Docker Compose

A partir da raiz:

```bash
docker compose config
docker compose up --build -d
docker compose ps
```

Verifique a API:

```bash
curl http://localhost:8000/api/health
```

Teste a análise:

```bash
curl -X POST http://localhost:8000/api/parse \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"x = 10\"}"
```

Encerre os serviços:

```bash
docker compose down
```

## 12. Próximas etapas

As próximas versões poderão incluir:
- Análise sintática.
- Análise semântica.
- Validação de declarações e expressões.
- Mais exemplos educacionais.
- Relatórios detalhados de erros.

## 13. Validação de instalação limpa

A validação deve ser realizada em uma cópia limpa do repositório,
seguindo somente os comandos documentados neste README.

Os resultados reais dos testes, as falhas e as correções devem
ser registrados em docs/TESTES.md.

Não declare testes como aprovados sem executar os comandos.
