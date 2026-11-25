
# Árvore Sintática Abstrata (AST)

## 1. Introdução

A Árvore Sintática Abstrata (AST) representa a estrutura hierárquica de um programa depois que o parser reconhece sua organização gramatical.

No Compiler Edu Tool, a AST é construída pelo analisador sintático descendente recursivo, implementado em Python.

Cada nó representa uma construção do subconjunto Mini-Python, como:

- Programa.
- Atribuição.
- Comando de saída.
- Condicional.
- Expressão binária.
- Expressão unária.
- Literal.
- Identificador.

A AST não executa o código-fonte. Ela representa sua estrutura sintática.

## 2. Diferença entre tokens, árvore de derivação e AST

### 2.1. Sequência de tokens

Os tokens são produzidos pelo analisador léxico.

Exemplo:

```python
resultado = 10 + 5 * 2
```

Representação simplificada:

```text
IDENTIFICADOR(resultado)
OPERADOR(=)
LITERAL_INTEIRO(10)
OPERADOR(+)
LITERAL_INTEIRO(5)
OPERADOR(*)
LITERAL_INTEIRO(2)
```

Os tokens representam as unidades identificadas no código-fonte, sem expressar completamente as relações sintáticas entre elas.

### 2.2. Árvore de derivação

A árvore de derivação, também chamada de árvore sintática concreta, representa a aplicação das produções da gramática.

Ela pode conter todos os símbolos terminais e não terminais utilizados durante o reconhecimento.

O projeto atual não gera uma árvore de derivação separada.

### 2.3. Árvore Sintática Abstrata

A AST simplifica a estrutura reconhecida, mantendo os elementos relevantes para representar o programa.

Para o código:

```python
resultado = 10 + 5 * 2
```

A estrutura conceitual é:

```text
Programa
└── Atribuicao
    ├── Identificador: resultado
    └── ExpressaoBinaria: +
        ├── Literal: 10
        └── ExpressaoBinaria: *
            ├── Literal: 5
            └── Literal: 2
```

A multiplicação aparece como filha da adição porque possui maior precedência.

## 3. Tipos de nós implementados

### 3.1. Programa

Representa o programa completo.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | Identifica o nó como `Programa` |
| corpo | Lista de comandos reconhecidos |

Exemplo:

```json
{
  "tipo": "Programa",
  "corpo": []
}
```

### 3.2. Atribuicao

Representa uma atribuição de valor a um identificador.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `Atribuicao` |
| identificador | Nome da variável |
| valor | Nó que representa a expressão atribuída |
| posicao | Linha e coluna inicial |

Exemplo:

```python
numero = 10
```

Representação:

```json
{
  "tipo": "Atribuicao",
  "identificador": "numero",
  "valor": {
    "tipo": "Literal",
    "valor": "10",
    "tipo_valor": "numero"
  },
  "posicao": {
    "linha": 1,
    "coluna": 1
  }
}
```

### 3.3. Print

Representa o comando de saída `print()`.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `Print` |
| expressao | Expressão apresentada pelo comando |
| posicao | Linha e coluna inicial |

Exemplo:

```python
print(numero)
```

### 3.4. Condicional

Representa uma estrutura `if/else`.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `Condicional` |
| condicao | Expressão utilizada na condição |
| corpo_if | Comandos executados no bloco do `if` |
| corpo_else | Comandos executados no bloco do `else` |
| posicao | Linha e coluna inicial |

Exemplo:

```python
if idade >= 18:
    print("Maior de idade")
else:
    print("Menor de idade")
```

### 3.5. ExpressaoBinaria

Representa uma operação com dois operandos.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `ExpressaoBinaria` |
| operador | Símbolo da operação |
| esquerda | Operando esquerdo |
| direita | Operando direito |
| posicao | Linha e coluna do operador |

Operadores suportados:

- `+`
- `-`
- `*`
- `/`
- `%`
- `==`
- `!=`
- `<`
- `>`
- `<=`
- `>=`

### 3.6. ExpressaoUnaria

Representa uma operação que utiliza um operando.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `ExpressaoUnaria` |
| operador | Operador unário |
| valor | Operando |
| posicao | Linha e coluna do operador |

Na versão atual, o operador unário implementado é o sinal negativo `-`.

### 3.7. Literal

Representa um valor constante.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `Literal` |
| valor | Lexema do literal |
| tipo_valor | Categoria do valor |
| posicao | Linha e coluna inicial |

Categorias atuais:

- `numero`
- `texto`

Os números inteiros e reais são identificados pelo scanner e representados como valores numéricos na AST.

### 3.8. Identificador

Representa o nome de uma variável utilizada em uma expressão.

Atributos:

| Atributo | Descrição |
|---|---|
| tipo | `Identificador` |
| nome | Nome identificado |
| posicao | Linha e coluna inicial |

## 4. Posições dos nós

Os nós criados pelo parser armazenam a posição inicial quando existe um token de referência.

A estrutura utilizada é:

```json
{
  "linha": 1,
  "coluna": 1
}
```

Essas posições permitem relacionar os elementos da AST com o código-fonte.

A implementação atual registra posições iniciais. As posições finais dos trechos ainda não fazem parte do formato da AST.

## 5. Exemplo completo de AST

Código de entrada:

```python
numero = 10
resultado = numero * 2
print(resultado)
```

Representação conceitual:

```text
Programa
├── Atribuicao
│   ├── Identificador: numero
│   └── Literal: 10
├── Atribuicao
│   ├── Identificador: resultado
│   └── ExpressaoBinaria: *
│       ├── Identificador: numero
│       └── Literal: 2
└── Print
    └── Identificador: resultado
```

O nó `Programa` agrupa os comandos. Cada atribuição possui um identificador e um valor. O comando `Print` contém a expressão que será apresentada.

## 6. Relação entre precedência e AST

Código:

```python
resultado = 10 + 5 * 2
```

A AST esperada é:

```text
Atribuicao
├── Identificador: resultado
└── ExpressaoBinaria: +
    ├── Literal: 10
    └── ExpressaoBinaria: *
        ├── Literal: 5
        └── Literal: 2
```

O parser utiliza funções diferentes para reconhecer os níveis de precedência.

A função de multiplicação é chamada durante o reconhecimento da soma. Por isso, a multiplicação é organizada como uma subárvore da adição.

## 7. Tratamento de erros

Quando a análise sintática encontra uma construção inválida, o parser registra:

- Mensagem explicativa.
- Linha do erro.
- Coluna do erro.
- Token encontrado.
- Elemento esperado, quando identificado.

A API deve apresentar a AST como nula quando a análise sintática não for bem-sucedida.

O parser realiza recuperação por sincronização no final da linha, permitindo continuar a análise de comandos posteriores em determinadas situações.

A recuperação não representa uma garantia de identificação de todos os erros de um mesmo comando. A implementação deve evitar apresentar diagnósticos em cascata.

## 8. Limitações atuais

A AST representa apenas as construções reconhecidas pela gramática do Mini-Python.

Ainda não existem nós específicos para:

- Declarações tipadas.
- Laços.
- Funções.
- Parâmetros.
- Retorno de funções.
- Listas e dicionários.
- Operações lógicas.

Esses elementos poderão ser incorporados em etapas posteriores.

## 9. Evolução prevista

A estrutura da AST poderá ser ampliada para armazenar:

- Posição inicial e final dos nós.
- Regras gramaticais associadas.
- Identificação dos trechos correspondentes no editor.
- Informações semânticas.
- Tipos de dados.
- Referências à tabela de símbolos.

A AST desta etapa servirá como base para a análise semântica da Etapa 5.
