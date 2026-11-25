# Compiler Edu Tool — Mini-Python

Software educacional para demonstrar etapas de um compilador por meio de uma aplicação web.

O projeto implementa análise léxica, análise sintática e construção de Árvore Sintática Abstrata (AST) para um subconjunto didático de Python denominado Mini-Python.

> O sistema não é um interpretador nem um compilador completo da linguagem Python.

## 1. Objetivo

O Compiler Edu Tool auxilia estudantes de Ciência da Computação na compreensão das etapas iniciais de um compilador.

O estudante informa um código-fonte, solicita a análise e visualiza:

- Tokens identificados pelo scanner.
- Estruturas sintáticas reconhecidas pelo parser.
- Árvore Sintática Abstrata.
- Erros léxicos e sintáticos.
- Posições dos elementos no código.
- Regras gramaticais relacionadas aos nós da AST.
- Destaque da linha correspondente ao nó selecionado.

A análise semântica será desenvolvida na Etapa 5.

## 2. Linguagem e escopo

A linguagem escolhida é um subconjunto didático de Python denominado Mini-Python.

### Construções reconhecidas

- Atribuições simples.
- Identificadores.
- Literais inteiros.
- Literais reais.
- Literais de texto.
- Expressões aritméticas.
- Expressões relacionais.
- Parênteses.
- Negação numérica unária.
- Comando `print()`.
- Condicionais `if/else`.
- Blocos definidos por indentação.
- Comentários iniciados por `#`.

### Construções fora do escopo

- Declarações tipadas, como `int x = 10`.
- Laços `while` e `for`.
- Funções e parâmetros.
- Comando `return`.
- Operadores lógicos `and`, `or` e `not`.
- Listas, tuplas e dicionários.
- Classes e orientação a objetos.
- Importação de módulos.
- Execução do código-fonte.
- Análise semântica.

A gramática completa está em `docs/gramatica.md`.

## 3. Tecnologias

### Backend

- Python 3.11.
- FastAPI.
- Uvicorn.
- Pytest.

### Frontend

- React 18.
- JavaScript.
- CSS.
- Jest.
- React Testing Library.

### Infraestrutura

- Docker.
- Docker Compose.

O scanner e o parser são implementados manualmente em Python. Não é utilizado um gerador externo de parser nesta versão.

## 4. Arquitetura

```text
ESTUDANTE
    |
    v
INTERFACE WEB (REACT)
    |
    | código-fonte
    v
BACKEND (FASTAPI)
    |
    v
ANALISADOR LÉXICO
    |
    | tokens e erros léxicos
    v
ANALISADOR SINTÁTICO
    |
    | AST e erros sintáticos
    v
RESPOSTA JSON
    |
    v
INTERFACE WEB
    |
    v
TOKENS / AST / ERROS
```

O processo de análise acontece em duas etapas principais:

1. O scanner identifica os tokens e verifica possíveis erros léxicos.
2. Quando não existem erros léxicos, o parser recebe os tokens e realiza a análise sintática, construindo a AST.

Quando o scanner encontra erros léxicos, o parser não é executado.

Essa decisão evita diagnósticos sintáticos derivados de tokens inválidos.

## 5. Estratégia do parser

O parser utiliza análise descendente recursiva (*Recursive Descent*).

Cada função representa uma parte da gramática.

| Função | Responsabilidade |
|---|---|
| `analisar()` | Processar o programa e construir a raiz da AST |
| `declaracao()` | Identificar o comando |
| `atribuicao()` | Reconhecer atribuições |
| `declaracao_print()` | Reconhecer o comando `print` |
| `declaracao_if()` | Reconhecer condicionais |
| `bloco_indentado()` | Processar blocos |
| `expressao()` | Reconhecer comparações |
| `soma()` | Reconhecer adições e subtrações |
| `multiplicacao()` | Reconhecer multiplicações, divisões e módulos |
| `fator()` | Reconhecer valores, identificadores, negação e parênteses |

O parser também utiliza funções auxiliares para consultar, consumir e avançar pelos tokens.

A estratégia foi escolhida por permitir relacionar diretamente as funções do código às produções gramaticais.

## 6. Precedência dos operadores

Da maior para a menor precedência:

1. Valores e parênteses.
2. Negação unária.
3. Multiplicação, divisão e módulo.
4. Adição e subtração.
5. Comparações.

As operações binárias são associadas à esquerda.

Exemplo:

```python
resultado = 10 + 5 * 2
```

A multiplicação é reconhecida antes da adição.

O parser também reconhece comparações encadeadas de acordo com sua implementação atual, construindo expressões binárias associadas à esquerda.

## 7. Árvore Sintática Abstrata

A AST representa a estrutura hierárquica reconhecida pelo parser.

Tipos de nós:

- `Programa`
- `Atribuicao`
- `Print`
- `Condicional`
- `ExpressaoBinaria`
- `ExpressaoUnaria`
- `Literal`
- `Identificador`

### Estrutura dos nós

| Tipo | Principais atributos |
|---|---|
| `Programa` | `corpo` |
| `Atribuicao` | `identificador`, `valor` |
| `Print` | `expressao` |
| `Condicional` | `condicao`, `corpo_if`, `corpo_else` |
| `ExpressaoBinaria` | `operador`, `esquerda`, `direita` |
| `ExpressaoUnaria` | `operador`, `valor` |
| `Literal` | `valor`, `tipo_valor` |
| `Identificador` | `nome` |

Os nós que possuem um token de origem armazenam a posição inicial por meio dos atributos `linha` e `coluna`, dentro de `posicao`.

A raiz `Programa` é criada sem posição própria.

### Exemplo de AST

Código:

```python
numero = 10
print(numero)
```

Representação simplificada:

```json
{
  "tipo": "Programa",
  "corpo": [
    {
      "tipo": "Atribuicao",
      "identificador": "numero",
      "valor": {
        "tipo": "Literal",
        "valor": "10",
        "tipo_valor": "numero",
        "posicao": {
          "linha": 1,
          "coluna": 10
        }
      },
      "posicao": {
        "linha": 1,
        "coluna": 1
      }
    },
    {
      "tipo": "Print",
      "expressao": {
        "tipo": "Identificador",
        "nome": "numero",
        "posicao": {
          "linha": 2,
          "coluna": 7
        }
      },
      "posicao": {
        "linha": 2,
        "coluna": 1
      }
    }
  ]
}
```

O projeto não gera uma árvore de derivação separada.

Consulte `docs/ast.md`.

## 8. Recursos da interface

A interface foi desenvolvida para permitir a visualização didática dos resultados da análise.

### Editor de código

- Inserção de código Mini-Python.
- Seleção de exemplos.
- Envio do código para análise.
- Exibição dos resultados.

### Visualização da AST

- Árvore hierárquica e navegável.
- Expansão e recolhimento dos nós.
- Seleção de nós.
- Exibição das propriedades dos nós.
- Filtro por tipo de nó.
- Exibição da regra gramatical relacionada.
- Identificação da linha e coluna do elemento selecionado.
- Destaque da linha correspondente no código.
- Exportação da AST em arquivo JSON.
- Cópia da AST em formato JSON.

### Visualização de tokens e erros

A interface também apresenta os tokens reconhecidos, incluindo os elementos estruturais de linha e indentação, além dos diagnósticos léxicos e sintáticos.

A AST não é disponibilizada quando a análise sintática apresenta erros.

## 9. Tratamento de erros

### Erros léxicos

São identificados pelo scanner e apresentados com informações como tipo, lexema, linha, coluna e mensagem.

Se houver erro léxico:

- O parser não é executado.
- Os diagnósticos são apresentados ao usuário.
- A AST é retornada como nula.

### Erros sintáticos

São identificados quando os tokens não correspondem à gramática.

Os diagnósticos incluem:

- Linha.
- Coluna.
- Elemento encontrado.
- Elemento esperado, quando identificado.
- Mensagem explicativa.

O parser utiliza sincronização no final da linha para tentar continuar a análise depois de determinados erros.

A recuperação é limitada e pode não identificar todos os erros de um mesmo comando.

Embora o parser possa produzir uma estrutura interna durante a recuperação, a API disponibiliza a AST somente quando a análise sintática termina sem erros.

### Análise semântica

Ainda não é realizada. O sistema não verifica declaração prévia de variáveis, compatibilidade de tipos ou validade semântica das operações.

Essas verificações pertencem à Etapa 5.

## 10. Estrutura do projeto

```text
compiler-edu-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── lexer.py
│   │   ├── scanner.py
│   │   ├── parser.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_lexer.py
│   │   ├── test_scanner.py
│   │   ├── test_parser.py
│   │   ├── test_main.py
│   │   └── test_deploy.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── App.test.js
│   │   ├── index.js
│   │   └── setupTests.js
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── gramatica.md
│   ├── ast.md
│   ├── materiais-metodos.md
│   ├── escopo-lexico.md
│   ├── tutorial-scanner.md
│   ├── TESTES.md
│   └── registro-de-testes.md
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 11. Pré-requisitos

Para executar a aplicação:

- Docker Desktop instalado.
- Docker Compose v2.
- Conexão com a internet na primeira construção das imagens.

Para executar testes fora do Docker:

- Python 3.11 ou superior.
- Node.js 18 ou superior.
- npm.

## 12. Executar a aplicação

Na raiz do projeto, execute:

```powershell
docker compose up --build -d
```

Confira os containers:

```powershell
docker compose ps
```

Consulte os logs:

```powershell
docker compose logs -f
```

Endereços:

| Serviço | Endereço |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Saúde da API | http://localhost:8000/api/health |

Para encerrar:

```powershell
docker compose down
```

## 13. API

### Endpoints

- `POST /api/parse`
- `POST /api/analyze`
- `GET /api/health`
- `GET /health`

### Requisição

O campo `code` é preferencial. O campo `codigo` permanece aceito para compatibilidade.

```json
{
  "code": "numero = 10\nprint(numero)"
}
```

### Campos da resposta

| Campo | Descrição |
|---|---|
| `message` | Mensagem geral da análise |
| `recebido` | Indica recebimento da requisição |
| `success` | Resultado geral, compatível com versões anteriores |
| `sucesso` | Resultado geral da análise |
| `tokens` | Tokens filtrados para compatibilidade com a Etapa 3 |
| `erros` | Lista de erros da análise |
| `tokens_parser` | Sequência completa produzida pelo scanner e consumida pelo parser |
| `sucesso_lexico` | Resultado da análise léxica |
| `erros_lexicos` | Diagnósticos do scanner |
| `sucesso_sintatico` | Resultado da análise sintática |
| `sintatico_executado` | Indica se o parser foi executado |
| `ast` | AST quando a análise sintática é bem-sucedida |
| `erros_sintaticos` | Diagnósticos do parser |
| `lexico` | Resultado agrupado da análise léxica |
| `sintatico` | Resultado agrupado da análise sintática |

A interface utiliza `tokens_parser` para apresentar a sequência completa, inclusive os elementos estruturais `NOVA_LINHA`, `INDENT` e `DEDENT`.

O campo `tokens` é mantido para compatibilidade com a etapa anterior.

### Exemplo ilustrativo de resposta com análise bem-sucedida

```json
{
  "message": "Análise léxica e sintática concluída com sucesso.",
  "recebido": true,
  "success": true,
  "sucesso": true,
  "tokens": [],
  "erros": [],
  "tokens_parser": [],
  "sucesso_lexico": true,
  "sucesso_sintatico": true,
  "sintatico_executado": true,
  "erros_lexicos": [],
  "ast": {
    "tipo": "Programa",
    "corpo": []
  },
  "erros_sintaticos": [],
  "lexico": {
    "sucesso": true,
    "tokens": [],
    "erros": []
  },
  "sintatico": {
    "executado": true,
    "sucesso": true,
    "ast": {
      "tipo": "Programa",
      "corpo": []
    },
    "erros": []
  }
}
```

Os arrays vazios e o corpo vazio da AST representam apenas a estrutura ilustrativa do contrato. Os valores reais dependem do código enviado.

### Comportamento em caso de erro léxico

- `sucesso_lexico` será falso.
- Os erros serão apresentados em `erros_lexicos`.
- O parser não será executado.
- `sintatico_executado` será falso.
- A AST será nula.

### Comportamento em caso de erro sintático

- `sucesso_lexico` será verdadeiro.
- `sucesso_sintatico` será falso.
- Os diagnósticos serão apresentados em `erros_sintaticos`.
- A AST será nula.

Entrada vazia retorna HTTP 400. Requisição sem `code` ou `codigo` retorna HTTP 422.

## 14. Testes do backend

Execute:

```powershell
docker compose exec backend pytest -vv
```

Somente parser:

```powershell
docker compose exec backend pytest tests/test_parser.py -vv
```

Somente endpoints:

```powershell
docker compose exec backend pytest tests/test_main.py -vv
```

Somente implantação:

```powershell
docker compose exec backend pytest tests/test_deploy.py -vv
```

## 15. Testes do frontend

Execute:

```powershell
docker compose exec -e CI=true frontend npm test -- --watchAll=false
```

Build de produção:

```powershell
docker compose exec frontend npm run build
```

## 16. Testes manuais

### Código válido

```python
numero = 10
resultado = numero * 2
print(resultado)
```

Resultado esperado:

- Análise léxica bem-sucedida.
- Análise sintática bem-sucedida.
- Tokens apresentados.
- AST gerada.

### Precedência

```python
resultado = 10 + 5 * 2
```

A multiplicação deve aparecer como subárvore da adição.

### Erro sintático

```python
numero = 10
resultado = numero *
print(resultado)
```

Resultado esperado:

- Análise léxica bem-sucedida.
- Erro sintático localizado.
- AST nula.

### Erro léxico

```python
numero = 10 @ 2
```

Resultado esperado:

- Erro léxico localizado.
- Parser não executado.
- AST nula.

### Condicional

```python
idade = 20

if idade >= 18:
    print("Maior de idade")
else:
    print("Menor de idade")
```

Resultado esperado:

- Condicional reconhecido.
- Blocos indentados identificados.
- AST com condição e corpos do `if` e `else`.

## 17. Documentação complementar

| Documento | Conteúdo |
|---|---|
| `docs/gramatica.md` | Gramática formal, terminais, não terminais e precedência |
| `docs/ast.md` | Nós, atributos, posições e exemplos |
| `docs/materiais-metodos.md` | Materiais, métodos, fluxograma e trabalhos relacionados |
| `docs/escopo-lexico.md` | Escopo do lexer |
| `docs/tutorial-scanner.md` | Tutorial de análise léxica e sintática |
| `docs/TESTES.md` | Procedimentos de validação |
| `docs/registro-de-testes.md` | Histórico de execuções e resultados |

## 18. Limitações conhecidas

- O projeto não implementa toda a linguagem Python.
- A gramática aceita somente as construções documentadas.
- A AST registra posições iniciais, mas não a extensão completa de cada trecho.
- A recuperação sintática é limitada.
- Não existe análise semântica nesta etapa.
- O código-fonte não é executado.
- A validação de ponta a ponta depende da execução dos testes e da demonstração no Docker.

## 19. Relação com a Etapa 5

A Etapa 4 entrega a estrutura sintática do programa.

A próxima etapa poderá utilizar a AST para implementar:

- Tabela de símbolos.
- Verificação de variáveis declaradas.
- Verificação de tipos.
- Compatibilidade de operações.
- Diagnósticos semânticos.

## 20. Diferencial opcional de IA

A integração com Ollama e Llama 3.2 é um diferencial opcional da atividade.

Ela não faz parte do fluxo obrigatório da análise léxica e sintática desta versão.

A aplicação principal não depende de um serviço de IA. Uma futura integração deverá utilizar o backend para acessar o Ollama, sem substituir os resultados oficiais do scanner e do parser.

## 21. Histórico de implementação

- Etapa 1: estrutura inicial, frontend, backend e Docker.
- Etapa 2: interface e comunicação frontend/backend.
- Etapa 3: analisador léxico e testes do scanner.
- Etapa 4: gramática, parser, AST, erros sintáticos, recursos interativos e integração com a interface.

A validação da Etapa 4 deve ser acompanhada pelo registro dos testes de backend, frontend, implantação e demonstração funcional.
