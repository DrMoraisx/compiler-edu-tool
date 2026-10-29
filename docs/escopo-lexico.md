# Escopo Léxico do Mini-Python

Este documento define exatamente o que o scanner reconhece. Ele é a base dos testes
(`backend/tests/test_lexer.py`) e da apresentação didática na interface.

## Categorias de token

| Categoria | Regra / Exemplos |
|---|---|
| `PALAVRA_RESERVADA` | `if`, `elif`, `else`, `while`, `def`, `return`, `print`, `and`, `or`, `not`, `True`, `False`, `None` (diferenciam maiúsculas e minúsculas) |
| `IDENTIFICADOR` | Letra ou `_`, seguida de letras, dígitos ou `_`. Ex.: `numero`, `resultado`, `_x1`, `área` |
| `LITERAL_INTEIRO` | Um ou mais dígitos. Ex.: `0`, `10`, `42` |
| `LITERAL_REAL` | Dígitos, ponto e dígitos. Ex.: `3.14`, `0.5` |
| `LITERAL_STRING` | Texto entre aspas simples ou duplas, em uma única linha, com `\` para escapar. Ex.: `"ola"`, `'ola'`. O lexema inclui as aspas |
| `OPERADOR` | Aritméticos: `+` `-` `*` `/` `//` `%` `**`. Relacionais: `==` `!=` `<` `>` `<=` `>=`. Atribuição: `=` `+=` `-=` `*=` `/=`. Lógicos: palavras reservadas `and`, `or`, `not` |
| `DELIMITADOR` | `(` `)` `:` `,` |
| `NOVA_LINHA` | Fim de uma linha com conteúdo (fim de comando) |
| `INDENTACAO` | A linha ficou mais recuada que a anterior (início de bloco) |
| `DESINDENTACAO` | O recuo diminuiu (fim de bloco). Os blocos abertos são fechados no fim do arquivo |

## Tratamento especial

| Item | Como o scanner trata |
|---|---|
| Espaços em branco | Ignorados (não geram tokens). Os espaços no início da linha definem a indentação |
| Tabulações | Expandidas para múltiplos de 4 colunas. As colunas informadas são as do texto já expandido |
| Linhas em branco | Ignoradas |
| Comentários | Comentário de linha com `#`, ignorado. Um `#` dentro de uma string não é comentário. O Python não possui comentário de bloco |
| Quebras de linha `\r\n` | Normalizadas para `\n` |
| Posição | Linha e coluna começam em 1; a coluna conta caracteres (não bytes) |

## Erros léxicos (o scanner não para: registra o erro e continua)

| Situação | Exemplo | Lexema reportado |
|---|---|---|
| Caractere não reconhecido | `x = 10 @ 2`, `;`, `$`, `?`, `{`, `[`, `.` | o caractere |
| String não terminada | `nome = "abc` | do abre-aspas até o fim da linha |
| Número malformado | `12abc` | o trecho inteiro (`12abc`) |
| Operador incompleto | `a ! b` | `!` (use `!=`) |
| Indentação inconsistente | recuo que não corresponde a nenhum nível anterior | os espaços iniciais |

Formato de cada erro:

```json
{
  "tipo": "ERRO_LEXICO",
  "lexema": "@",
  "linha": 2,
  "coluna": 10,
  "mensagem": "Caractere não reconhecido '@'. Verifique se ele faz parte do subconjunto suportado."
}
```

## Fora do escopo desta etapa

Listas e dicionários (`[ ] { }`), ponto (`.`), strings de várias linhas (aspas triplas),
prefixos de string (`f"..."`), notação científica (`1e3`), números em outras bases e
literais complexos.