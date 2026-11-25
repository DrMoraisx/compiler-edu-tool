
# Tutorial: análise léxica e sintática do Mini-Python

Tutorial educacional do Compiler Edu Tool.

## 1. O que é um compilador?

Um compilador é um programa que analisa um código-fonte para verificar sua estrutura e, em etapas posteriores, seu significado.

Nesta versão do Compiler Edu Tool, são trabalhadas duas etapas:

1. Análise léxica.
2. Análise sintática.

A análise semântica será desenvolvida na Etapa 5.

## 2. Análise léxica

A análise léxica é responsável por ler o código-fonte e identificar suas unidades mínimas, chamadas tokens.

Exemplo:

```python
numero = 10
```

O scanner reconhece:

| Lexema | Tipo | Linha | Coluna |
|---|---|---|---|
| `numero` | IDENTIFICADOR | 1 | 1 |
| `=` | OPERADOR | 1 | 8 |
| `10` | LITERAL_INTEIRO | 1 | 10 |

O lexema é o texto encontrado no código. O tipo indica a categoria à qual ele pertence.

## 3. Como o scanner reconhece os tokens?

O scanner percorre o código da esquerda para a direita.

De acordo com o caractere encontrado, identifica se o próximo elemento é:

- Uma palavra reservada.
- Um identificador.
- Um número.
- Uma string.
- Um operador.
- Um delimitador.

Também registra a linha e a coluna de cada token.

Espaços e comentários são ignorados.

## 4. Análise sintática

Depois da análise léxica, os tokens são enviados ao parser.

O parser verifica se a sequência de tokens respeita a gramática do Mini-Python.

Exemplo:

```python
numero = 10
print(numero)
```

O scanner identifica os tokens.

O parser reconhece duas construções:

1. Uma atribuição.
2. Um comando de saída.

A análise sintática organiza esses elementos em uma estrutura hierárquica.

## 5. O que é uma AST?

AST significa Árvore Sintática Abstrata.

Ela representa a estrutura do programa por meio de nós.

Exemplo:

```python
resultado = 10 + 5 * 2
```

Representação simplificada:

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

A multiplicação aparece dentro da soma porque possui maior precedência.

## 6. Precedência dos operadores

A precedência determina qual operação é reconhecida primeiro.

No subconjunto atual:

1. Parênteses e valores.
2. Negação unária.
3. Multiplicação, divisão e módulo.
4. Adição e subtração.
5. Comparações.

Exemplo:

```python
resultado = 10 + 5 * 2
```

O parser reconhece primeiro `5 * 2` e depois a soma com `10`.

Os parênteses podem alterar o agrupamento:

```python
resultado = (10 + 5) * 2
```

## 7. Condicionais e indentação

O Mini-Python utiliza indentação para representar blocos.

Exemplo:

```python
idade = 20

if idade >= 18:
    print("Maior de idade")
else:
    print("Menor de idade")
```

O scanner produz tokens estruturais para indicar:

- Fim de linha.
- Início de bloco.
- Final de bloco.

O parser utiliza esses tokens para identificar o conteúdo do `if` e do `else`.

## 8. Entendendo os erros

### 8.1. Erro léxico

Exemplo:

```python
numero = 10 @ 2
```

O caractere `@` não pertence ao subconjunto reconhecido pelo lexer principal.

O scanner registra o erro com linha e coluna.

O parser não é executado quando existem erros léxicos.

### 8.2. Erro sintático

Exemplo:

```python
resultado = 10 +
```

O scanner consegue identificar os tokens, mas o parser encontra uma expressão incompleta.

O diagnóstico informa a localização, o elemento encontrado e o elemento esperado, quando identificado.

### 8.3. Parêntese não fechado

Exemplo:

```python
print((10 + 5)
```

A expressão não possui todos os delimitadores necessários.

O parser identifica a construção incompleta e registra um erro sintático.

## 9. Como utilizar a interface

1. Abra a aplicação no navegador.
2. Escolha um dos exemplos disponíveis ou digite um código.
3. Clique em **ANALISAR CÓDIGO**.
4. Consulte a aba **Árvore AST** para visualizar a estrutura reconhecida.
5. Selecione um nó para consultar sua posição e regra gramatical.
6. Utilize os controles para expandir ou recolher a árvore.
7. Consulte a aba **Tokens** para ver os elementos reconhecidos pelo scanner.
8. Consulte a aba **Erros** para verificar os diagnósticos.
9. Consulte a aba **Gramática** para visualizar as principais regras.
10. Utilize a aba **JSON** para consultar a resposta estruturada.

A AST pode ser exportada em formato JSON quando a análise sintática for bem-sucedida.

## 10. Limitações do subconjunto

A aplicação não implementa toda a linguagem Python.

Não são reconhecidos sintaticamente nesta versão:

- Laços `while` e `for`.
- Definições de funções.
- Parâmetros e retorno.
- Declarações tipadas.
- Operadores lógicos.
- Listas e dicionários.
- Classes.
- Importações.

O código não é executado. A aplicação realiza análise léxica e sintática.

## 11. Próxima etapa

Na Etapa 5, a AST poderá ser utilizada para implementar análise semântica, como:

- Verificação de variáveis declaradas.
- Tabela de símbolos.
- Compatibilidade de tipos.
- Validação de operações.
- Diagnósticos semânticos.
