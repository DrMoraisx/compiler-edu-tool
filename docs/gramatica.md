
# Gramática Formal do Mini-Python

## 1. Objetivo

Este documento especifica a gramática do subconjunto didático da linguagem Mini-Python reconhecido pelo Compiler Edu Tool.

A gramática é utilizada pelo analisador sintático (parser) para verificar a organização dos tokens produzidos pelo analisador léxico e construir a Árvore Sintática Abstrata (AST).

O projeto não implementa toda a linguagem Python. São reconhecidas apenas as construções descritas neste documento.

## 2. Símbolo inicial

O símbolo inicial da gramática é:

`programa`

A análise começa nesse símbolo e termina quando todos os comandos e tokens estruturais do código-fonte forem consumidos.

## 3. Terminais e não terminais

### 3.1. Terminais

Os terminais representam os elementos concretos reconhecidos pelo scanner.

| Terminal | Descrição |
|---|---|
| IDENTIFICADOR | Nome de variável |
| LITERAL_INTEIRO | Número inteiro |
| LITERAL_REAL | Número decimal |
| LITERAL_STRING | Texto entre aspas |
| OPERADOR | Operadores aritméticos e relacionais |
| PALAVRA_RESERVADA(print) | Comando de saída |
| PALAVRA_RESERVADA(if) | Condicional |
| PALAVRA_RESERVADA(else) | Alternativa do condicional |
| DELIMITADOR | Parênteses e dois-pontos |
| NOVA_LINHA | Final de linha |
| INDENT | Início de bloco indentado |
| DEDENT | Final de bloco indentado |
| EOF | Fim da entrada |

### 3.2. Não terminais

| Não terminal | Responsabilidade |
|---|---|
| programa | Representa o programa completo |
| declaracao | Representa um comando |
| atribuicao | Representa uma atribuição |
| comando_print | Representa uma chamada de print |
| condicional | Representa if/else |
| bloco | Representa uma sequência indentada de comandos |
| expressao | Representa uma expressão completa |
| soma | Representa adição e subtração |
| multiplicacao | Representa multiplicação, divisão e módulo |
| fator | Representa valores, identificadores e expressões agrupadas |

## 4. Gramática em EBNF

A notação utilizada é EBNF.

```ebnf
programa        = { nova_linha | declaracao } ;

declaracao      = atribuicao
                | comando_print
                | condicional ;

atribuicao      = IDENTIFICADOR, "=", expressao ;

comando_print   = "print", "(", expressao, ")" ;

condicional     = "if", expressao, ":", nova_linha,
                  INDENT, bloco, DEDENT,
                  [ "else", ":", nova_linha,
                    INDENT, bloco, DEDENT ] ;

bloco           = { nova_linha | declaracao } ;

expressao       = soma, { operador_comparacao, soma } ;

soma            = multiplicacao,
                  { operador_soma, multiplicacao } ;

multiplicacao   = fator,
                  { operador_multiplicacao, fator } ;

fator           = literal
                | IDENTIFICADOR
                | "-", fator
                | "(", expressao, ")" ;

literal         = LITERAL_INTEIRO
                | LITERAL_REAL
                | LITERAL_STRING ;

operador_comparacao =
                    "=="
                  | "!="
                  | "<"
                  | ">"
                  | "<="
                  | ">=" ;

operador_soma   = "+" | "-" ;

operador_multiplicacao =
                    "*"
                  | "/"
                  | "%" ;

nova_linha      = NOVA_LINHA ;
```

Observação: a gramática é uma representação formal do subconjunto implementado. Os tokens `INDENT`, `DEDENT` e `NOVA_LINHA` são produzidos pelo analisador léxico para representar a estrutura dos blocos e das linhas.

## 5. Correspondência entre gramática e scanner

O scanner reconhece os elementos léxicos e entrega ao parser uma sequência de tokens.

A correspondência utilizada é:

| Elemento da gramática | Tipo de token |
|---|---|
| IDENTIFICADOR | IDENTIFICADOR |
| Número inteiro | LITERAL_INTEIRO |
| Número decimal | LITERAL_REAL |
| Texto | LITERAL_STRING |
| `if`, `else`, `print` | PALAVRA_RESERVADA |
| `=`, `+`, `-`, `*`, `/`, `%` | OPERADOR |
| `==`, `!=`, `<`, `>`, `<=`, `>=` | OPERADOR |
| `(`, `)`, `:` | DELIMITADOR |
| Quebra de linha | NOVA_LINHA |
| Aumento de indentação | INDENT |
| Redução de indentação | DEDENT |

Os espaços em branco e comentários iniciados por `#` são ignorados pelo scanner.

## 6. Precedência e associatividade

O parser utiliza funções separadas para reconhecer os níveis de precedência.

Da maior para a menor precedência:

| Nível | Operadores | Associatividade |
|---|---|---|
| 1 | Parênteses e valores | Não aplicável |
| 2 | `-` unário | À direita |
| 3 | `*`, `/`, `%` | À esquerda |
| 4 | `+`, `-` | À esquerda |
| 5 | `==`, `!=`, `<`, `>`, `<=`, `>=` | À esquerda |

### 6.1. Exemplo de precedência

Código:

```python
resultado = 10 + 5 * 2
```

A estrutura reconhecida deve ser equivalente a:

```text
Adicao
├── Literal: 10
└── Multiplicacao
    ├── Literal: 5
    └── Literal: 2
```

A multiplicação é reconhecida primeiro, pois possui precedência maior que a adição.

### 6.2. Exemplo de associatividade

Código:

```python
resultado = 20 - 5 - 3
```

A estrutura é equivalente a:

```text
Subtracao
├── Subtracao
│   ├── Literal: 20
│   └── Literal: 5
└── Literal: 3
```

A expressão é agrupada da esquerda para a direita.

### 6.3. Uso de parênteses

Código:

```python
resultado = (10 + 5) * 2
```

Os parênteses alteram o agrupamento:

```text
Multiplicacao
├── Adicao
│   ├── Literal: 10
│   └── Literal: 5
└── Literal: 2
```

## 7. Construções suportadas

O subconjunto atual reconhece:

- Atribuição simples de variáveis.
- Literais inteiros.
- Literais reais.
- Literais de texto.
- Identificadores.
- Comando `print()` com uma expressão.
- Condicional `if`.
- Alternativa `else`.
- Blocos delimitados por indentação.
- Expressões aritméticas.
- Expressões relacionais.
- Expressões entre parênteses.
- Operação unária de negação numérica.
- Comentários iniciados por `#`.
- Programas com múltiplas linhas.
- Condicionais e comandos aninhados.

## 8. Construções fora do escopo atual

As seguintes construções não são reconhecidas pelo parser atual:

- Declarações tipadas como `int x = 10`.
- Laços `while` e `for`.
- Definições de funções com `def`.
- Comando `return`.
- Operadores lógicos `and`, `or` e `not`.
- Listas, tuplas e dicionários.
- Acesso a índices e atributos.
- Chamadas de funções diferentes de `print`.
- Atribuições compostas como `+=` e `-=`.
- Importações de módulos.
- Classes e orientação a objetos.
- Expressões condicionais completas da linguagem Python.
- Execução ou interpretação do código-fonte.

Essas construções poderão ser incorporadas em etapas futuras, mediante atualização da gramática, do parser e dos testes.

## 9. Exemplos válidos

### Exemplo 1 — Atribuição

```python
numero = 10
```

### Exemplo 2 — Expressão aritmética

```python
resultado = 10 + 5 * 2
```

### Exemplo 3 — Saída

```python
nome = "Maria"
print(nome)
```

### Exemplo 4 — Condicional

```python
idade = 20

if idade >= 18:
    print("Maior de idade")
else:
    print("Menor de idade")
```

### Exemplo 5 — Expressão com parênteses

```python
resultado = (10 + 5) * 2
```

## 10. Exemplos inválidos

### Exemplo 1 — Expressão incompleta

```python
resultado = 10 +
```

Problema: falta um operando depois do operador `+`.

### Exemplo 2 — Parêntese não fechado

```python
print((10 + 5)
```

Problema: falta um parêntese de fechamento.

### Exemplo 3 — Comando não reconhecido

```python
while numero > 0:
    print(numero)
```

Problema: `while` não pertence às construções sintáticas implementadas nesta versão.

### Exemplo 4 — Atribuição sem expressão

```python
numero =
```

Problema: falta uma expressão depois do operador de atribuição.

## 11. Estratégia de análise sintática

O projeto utiliza análise descendente recursiva (Recursive Descent).

Cada função do parser representa uma parte da gramática. Por exemplo:

- `analisar()` processa o programa.
- `declaracao()` identifica o tipo de comando.
- `atribuicao()` reconhece atribuições.
- `declaracao_print()` reconhece comandos de saída.
- `declaracao_if()` reconhece condicionais.
- `expressao()` reconhece comparações.
- `soma()` reconhece adições e subtrações.
- `multiplicacao()` reconhece multiplicações, divisões e módulos.
- `fator()` reconhece literais, identificadores e expressões agrupadas.

A estratégia foi escolhida por ser simples de compreender, implementar e demonstrar didaticamente.

## 12. Tratamento de erros léxicos

Quando o scanner identifica um erro léxico, o parser não é executado.

Essa decisão evita que caracteres inválidos ou tokens incompletos provoquem diagnósticos sintáticos sem significado.

Os erros léxicos continuam sendo apresentados ao estudante, com mensagem, linha e coluna.

## 13. Limitações

O parser reconhece somente as produções descritas neste documento.

A análise sintática não verifica se as variáveis foram declaradas anteriormente, se os tipos são compatíveis ou se uma operação possui significado válido.

Essas verificações pertencem à análise semântica, prevista para a Etapa 5.

## 14. Evolução da gramática

A inclusão de novas construções deverá seguir este fluxo:

1. Atualizar a gramática formal.
2. Verificar se o scanner reconhece os terminais necessários.
3. Implementar a produção correspondente no parser.
4. Definir os nós necessários na AST.
5. Criar testes unitários e de integração.
6. Atualizar a interface e a documentação.
7. Executar os testes de regressão.
