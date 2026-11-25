
# Escopo Léxico do Mini-Python

## 1. Objetivo

Este documento define os elementos léxicos reconhecidos pelo analisador utilizado no fluxo principal do Compiler Edu Tool.

O analisador léxico identifica os tokens presentes no código-fonte e registra erros com localização.

O módulo utilizado pela API é:

`backend/app/lexer.py`

A função utilizada pelo backend é:

`analisar_lexico(codigo)`

## 2. Palavras reservadas

O analisador principal reconhece as seguintes palavras reservadas:

| Palavra | Utilização sintática |
|---|---|
| `if` | Início de condicional |
| `else` | Alternativa de condicional |
| `print` | Comando de saída |

A classificação diferencia maiúsculas e minúsculas.

Palavras como `while`, `for`, `def`, `return`, `and`, `or`, `not`, `True`, `False` e `None` não são palavras reservadas no lexer principal desta versão.

Mesmo que alguns desses lexemas sejam identificados como identificadores, isso não significa que sejam aceitos pelo parser.

## 3. Categorias de tokens

| Categoria | Regra ou exemplos |
|---|---|
| `PALAVRA_RESERVADA` | `if`, `else`, `print` |
| `IDENTIFICADOR` | Letras ou `_`, seguidos de letras, números ou `_` |
| `LITERAL_INTEIRO` | `0`, `10`, `42` |
| `LITERAL_REAL` | `3.14`, `0.5`, `10.0` |
| `LITERAL_STRING` | `"texto"` ou `'texto'` |
| `OPERADOR` | `+`, `-`, `*`, `/`, `%`, `=`, `<`, `>` |
| `OPERADOR` | `==`, `!=`, `<=`, `>=`, `+=`, `-=`, `*=`, `/=` |
| `DELIMITADOR` | `(`, `)`, `:`, `,` |
| `NOVA_LINHA` | Final de linha com conteúdo |
| `INDENT` | Início de bloco indentado |
| `DEDENT` | Encerramento de bloco indentado |

Os operadores compostos são reconhecidos antes dos operadores simples.

## 4. Identificadores

Um identificador pode começar com uma letra ou sublinhado.

Os caracteres seguintes podem conter letras, números ou sublinhados.

Exemplos válidos:

```python
numero
resultado
_x1
soma_total
área
```

Exemplos inválidos:

```python
1numero
9_x
```

## 5. Literais numéricos

### 5.1. Inteiros

São formados por um ou mais dígitos.

Exemplos:

```python
0
10
42
2048
```

### 5.2. Reais

São formados por dígitos, ponto e dígitos.

Exemplos:

```python
3.14
0.5
10.0
123.456
```

A notação científica não faz parte do subconjunto atual.

## 6. Literais textuais

Strings são delimitadas por aspas simples ou duplas.

Exemplos:

```python
nome = "Maria"
mensagem = 'Olá'
texto = "Texto com espaços"
```

O lexema do token inclui as aspas.

O scanner permite o uso de barra invertida para escapar caracteres dentro da string.

Strings de múltiplas linhas não são suportadas.

## 7. Operadores

### 7.1. Operadores simples

| Operador | Categoria de uso |
|---|---|
| `+` | Adição |
| `-` | Subtração ou negação unária |
| `*` | Multiplicação |
| `/` | Divisão |
| `%` | Módulo |
| `=` | Atribuição |
| `<` | Comparação |
| `>` | Comparação |

### 7.2. Operadores compostos

| Operador | Descrição |
|---|---|
| `==` | Igualdade |
| `!=` | Diferença |
| `<=` | Menor ou igual |
| `>=` | Maior ou igual |
| `+=` | Atribuição composta |
| `-=` | Atribuição composta |
| `*=` | Atribuição composta |
| `/=` | Atribuição composta |

Atenção: o reconhecimento léxico de um operador não significa que ele seja aceito sintaticamente.

Os operadores `+=`, `-=`, `*=` e `/=` são reconhecidos pelo lexer, mas não possuem produção de atribuição correspondente no parser atual.

## 8. Delimitadores

O lexer principal reconhece:

- `(`
- `)`
- `:`
- `,`

Colchetes, chaves, ponto e ponto e vírgula não pertencem ao subconjunto léxico utilizado pela API.

## 9. Comentários e espaços

Comentários começam com `#` e continuam até o final da linha.

Exemplo:

```python
# comentário
numero = 10  # comentário após comando
```

Um caractere `#` dentro de uma string não inicia comentário.

Espaços em branco não geram tokens. A indentação inicial da linha é utilizada para identificar blocos.

Tabulações são expandidas para quatro espaços.

Linhas vazias e linhas contendo somente comentários são ignoradas.

## 10. Tokens estruturais

O lexer gera tokens estruturais para que o parser reconheça a organização dos blocos.

| Token | Significado |
|---|---|
| `NOVA_LINHA` | Fim de uma linha com conteúdo |
| `INDENTACAO` | Aumento da indentação |
| `DESINDENTACAO` | Redução da indentação |

A função `analisar_lexico()` converte os nomes internos:

- `INDENTACAO` para `INDENT`.
- `DESINDENTACAO` para `DEDENT`.

Os blocos abertos são fechados no fim do arquivo.

## 11. Posições

As posições dos tokens começam em 1.

Cada token contém:

- Tipo.
- Lexema.
- Linha.
- Coluna.

As posições são utilizadas pelo parser para localizar os nós da AST e os erros.

## 12. Erros léxicos

O scanner registra os erros encontrados e continua a leitura quando possível.

| Situação | Exemplo | Diagnóstico |
|---|---|---|
| Caractere não reconhecido | `x = 10 @ 2` | Caractere fora do subconjunto |
| String não terminada | `nome = "abc` | String não terminada |
| Número malformado | `12abc` | Número malformado |
| Exclamação isolada | `a ! b` | Sugestão de uso de `!=` |
| Indentação inconsistente | Recuo incompatível | Erro de indentação |

Formato de erro:

```json
{
  "tipo": "ERRO_LEXICO",
  "lexema": "@",
  "linha": 1,
  "coluna": 10,
  "mensagem": "Caractere não reconhecido."
}
```

## 13. Integração com o parser

O fluxo principal é:

1. A API recebe o código.
2. O lexer identifica tokens e erros.
3. A API apresenta os tokens.
4. Se houver erro léxico, o parser não é executado.
5. Se não houver erro léxico, os tokens completos são enviados ao parser.
6. O parser utiliza `INDENT`, `DEDENT` e `NOVA_LINHA` para reconhecer os blocos.

A decisão de não executar o parser após erros léxicos evita diagnósticos sintáticos causados por uma sequência de tokens inválida.

## 14. Módulo de compatibilidade da Etapa 3

O projeto também mantém:

`backend/app/scanner.py`

Esse módulo possui uma interface de scanner preservada para os testes de compatibilidade da etapa anterior e reconhece um conjunto mais amplo de palavras e delimitadores.

O fluxo principal da API utiliza `lexer.py`, pois ele produz os tokens estruturais necessários ao parser atual.

Os dois módulos não devem ser confundidos ao interpretar os resultados dos testes.

## 15. Fora do escopo

Não fazem parte do lexer principal desta versão:

- Strings de múltiplas linhas.
- Prefixos de string.
- Notação científica.
- Números em outras bases.
- Literais complexos.
- Colchetes e acesso a índices.
- Dicionários.
- Ponto e acesso a atributos.
- Ponto e vírgula.
- Operadores lógicos.
- Palavras reservadas de construções ainda não implementadas.
