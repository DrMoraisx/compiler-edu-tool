
# Testes e validação — Compiler Edu Tool

## 1. Objetivo

Este documento descreve como executar os testes automatizados e validar o funcionamento do Compiler Edu Tool.

Os testes são organizados em:

- Testes unitários do lexer.
- Testes unitários do scanner de compatibilidade.
- Testes unitários do parser.
- Testes dos endpoints.
- Testes da interface.
- Testes de implantação.
- Testes de regressão.

## 2. Testes do backend

Com os containers ativos, execute:

```powershell
docker compose exec backend pytest -vv
```

### 2.1. Lexer

Arquivo:

`backend/tests/test_lexer.py`

Verifica:

- Palavras reservadas.
- Identificadores.
- Literais inteiros.
- Literais reais.
- Strings.
- Operadores simples.
- Operadores compostos.
- Delimitadores.
- Comentários.
- Espaços em branco.
- Indentação e desindentação.
- Posições de tokens.
- Caracteres inválidos.
- Strings não terminadas.
- Números malformados.
- Acúmulo de erros léxicos.
- Casos de borda.

### 2.2. Scanner de compatibilidade

Arquivo:

`backend/tests/test_scanner.py`

Verifica a interface de scanner mantida para compatibilidade com a Etapa 3.

### 2.3. Parser

Arquivo:

`backend/tests/test_parser.py`

Verifica:

- Atribuições.
- Comando `print`.
- Literais numéricos e textuais.
- Expressões aritméticas.
- Expressões relacionais.
- Precedência.
- Associatividade.
- Parênteses.
- Operação unária.
- Condicionais.
- Condicionais aninhados.
- Blocos indentados.
- Posições da AST.
- Expressões incompletas.
- Parênteses não fechados.
- Comandos fora do escopo.
- Recuperação entre linhas.
- Programa vazio.

### 2.4. Endpoints

Arquivo:

`backend/tests/test_main.py`

Verifica:

- Endpoint raiz.
- Endpoint `/api/health`.
- Alias `/health`.
- Endpoint `/api/parse`.
- Alias `/api/analyze`.
- Recebimento dos campos `code` e `codigo`.
- Resposta para código válido.
- Erros léxicos.
- Erros sintáticos.
- AST nula em caso de erro sintático.
- Não execução do parser após erro léxico.
- Contrato agrupado `lexico` e `sintatico`.
- Entrada vazia.
- Requisição inválida.

## 3. Testes de implantação

Arquivo:

`backend/tests/test_deploy.py`

Comando:

```powershell
docker compose exec backend pytest tests/test_deploy.py -vv
```

Os testes verificam os serviços reais:

- Backend acessível.
- Endpoint de saúde.
- Recebimento de código.
- Rejeição de entrada vazia.
- Análise completa.
- Erro sintático com AST nula.
- Erro léxico sem execução do parser.
- Frontend acessível.

Os testes de implantação dependem dos containers em execução.

Se um serviço não estiver acessível, o teste correspondente poderá ser ignorado. Um teste ignorado não deve ser contabilizado como aprovado.

## 4. Testes do frontend

Arquivo:

`frontend/src/App.test.js`

Comando:

```powershell
docker compose exec -e CI=true frontend npm test -- --watchAll=false
```

Os testes verificam:

- Exibição do editor.
- Exibição do botão de análise.
- Seleção de exemplos.
- Validação de entrada vazia.
- Envio ao endpoint.
- Exibição dos tokens.
- Exibição da AST.
- Seleção de nós.
- Exibição da regra gramatical.
- Expansão e recolhimento da árvore.
- Exibição de erros sintáticos.
- Exibição de linha e coluna.
- Distinção entre erro léxico e sintático.
- Mensagem de falha de comunicação.

## 5. Build do frontend

Execute:

```powershell
docker compose exec frontend npm run build
```

O comando verifica se a aplicação React pode ser compilada para produção.

## 6. Validação do Docker Compose

Na raiz do projeto:

```powershell
docker compose config
docker compose up --build -d
docker compose ps
```

Verifique a saúde do backend:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

Acesse:

- http://localhost:3000
- http://localhost:8000/docs

## 7. Testes manuais funcionais

### 7.1. Código válido

```python
numero = 10
resultado = numero * 2
print(resultado)
```

Verificar:

- Sucesso léxico.
- Sucesso sintático.
- Tokens apresentados.
- AST gerada.
- Estrutura coerente com o código.

### 7.2. Precedência

```python
resultado = 10 + 5 * 2
```

Verificar se a multiplicação aparece como subárvore da adição.

### 7.3. Erro sintático

```python
resultado = numero *
```

Verificar:

- Análise léxica bem-sucedida.
- Análise sintática com erro.
- Mensagem explicativa.
- Linha e coluna.
- AST nula.

### 7.4. Erro léxico

```python
numero = 10 @ 2
```

Verificar:

- Erro léxico localizado.
- Parser não executado.
- AST nula.
- Aplicação continua funcionando.

### 7.5. Condicional

```python
idade = 20

if idade >= 18:
    print("Maior de idade")
else:
    print("Menor de idade")
```

Verificar:

- Reconhecimento do `if`.
- Reconhecimento do `else`.
- Blocos indentados.
- AST com condição e corpos.

## 8. Critérios de aprovação

A validação técnica deve observar:

| Critério | Condição de aprovação |
|---|---|
| Lexer | Testes léxicos aprovados |
| Parser | Testes sintáticos aprovados |
| API | Contrato e códigos HTTP corretos |
| AST | Estrutura coerente e posições disponíveis |
| Erros | Diagnósticos localizados |
| Frontend | Testes de interface aprovados |
| Integração | Frontend e backend comunicam-se |
| Docker | Serviços iniciam corretamente |
| Regressão | Testes das etapas anteriores preservados |

## 9. Registro dos resultados

Os resultados reais devem ser registrados em:

`docs/registro-de-testes.md`

Registrar:

- Data.
- Comando executado.
- Quantidade de testes aprovados.
- Quantidade de falhas.
- Quantidade de testes ignorados.
- Correções realizadas.
- Pendências.

Não declarar validação integral se alguma categoria de teste ainda não foi executada.

## 10. Limitações

Os testes automatizados verificam o comportamento técnico do software.

Eles não demonstram, isoladamente, melhoria de aprendizagem ou eficácia pedagógica. Para isso, seria necessário realizar uma avaliação com estudantes e registrar os resultados.
