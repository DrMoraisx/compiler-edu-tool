# Tutorial: entendendo o analisador léxico (scanner)

Tutorial inicial para quem está aprendendo compiladores com o **EDUTER_TOOL**.

## 1. O que é um scanner?
Um compilador não "entende" o código de uma vez. Ele trabalha em fases. A primeira é a
**análise léxica**: ler o texto caractere por caractere e separá-lo em pedaços com significado.
Esses pedaços são os **tokens**. O programa que faz isso se chama **scanner** (ou lexer).

## 2. Token e lexema
- **Lexema:** o trecho exato do código. Em `numero = 10`, os lexemas são `numero`, `=` e `10`.
- **Token:** o lexema classificado em uma **categoria**, com a posição onde apareceu.

| Lexema | Categoria do token | Linha | Coluna |
|---|---|---|---|
| `numero` | `IDENTIFICADOR` | 1 | 1 |
| `=` | `OPERADOR` | 1 | 8 |
| `10` | `LITERAL_INTEIRO` | 1 | 10 |

## 3. Como o scanner percorre o código
1. Pula espaços e comentários.
2. Olha o caractere atual para decidir o que está começando: uma letra (palavra ou nome), um dígito
   (número), uma aspa (string) ou um símbolo (operador ou delimitador).
3. Continua lendo enquanto os caracteres seguintes ainda pertencem ao mesmo lexema.
4. Classifica o lexema e guarda linha e coluna.
5. Repete até o fim do código.

Exemplo com `y = 3.5`:

```
y   -> começa com letra          -> IDENTIFICADOR
=   -> símbolo de atribuição     -> OPERADOR
3.5 -> dígito, ponto, dígito     -> LITERAL_REAL
```

## 4. Palavra reservada ou identificador?
O scanner lê a palavra inteira e depois consulta a lista de palavras reservadas.
`if` é `PALAVRA_RESERVADA`, mas `iffy` é `IDENTIFICADOR`. Maiúsculas importam: `True` é reservada, `true` não.

## 5. A indentação do Python também gera tokens
Em Python, o recuo define os blocos. Por isso o scanner emite `NOVA_LINHA` (fim da linha),
`INDENTACAO` (recuo aumentou) e `DESINDENTACAO` (recuo diminuiu). Na interface eles aparecem
em cinza, com os símbolos ↵, → e ←.

## 6. Erros léxicos
O scanner reporta o que não consegue reconhecer, **sem parar**, para que você veja todos os
problemas de uma vez. Experimente o **Exemplo 5**:

```python
preco = 10 @ 2          # '@' não faz parte da linguagem
nome = "sem fechar      # string sem aspas de fechamento
valor = 12abc           # número malformado
```

## 7. Roteiro para praticar na ferramenta
1. Escolha o **Exemplo 1** e clique em **ANALISAR CÓDIGO**.
2. Abra **TOKENS** e confira tipo, lexema, linha e coluna de cada um.
3. Abra **CÓDIGO COLORIDO** e compare o código original com a sequência de tokens.
4. Abra **PASSO A PASSO** e use **Próximo** para ver o scanner lendo um token por vez.
5. Carregue o **Exemplo 6** (todas as categorias) e o **Exemplo 5** (erros).
6. Escreva seu próprio código, insira um erro de propósito e observe a mensagem.

## 8. E depois?
O scanner só reconhece tokens: ele não verifica se o programa está bem estruturado.
Isso é papel do **analisador sintático** (próxima etapa). Por exemplo, `if if if` é
tokenizado normalmente, pois todos os tokens são válidos.