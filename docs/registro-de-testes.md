# Registro de Testes — Compiler Edu Tool

## 1. Objetivo

Este documento registra as execuções dos testes automatizados, as validações realizadas, as correções e as pendências do Compiler Edu Tool.

Os resultados apresentados correspondem às saídas dos comandos executados durante a validação da Etapa 4 — Análise Sintática e AST.

## 2. Testes do backend

### Execução em 25/11/2026

Comando:

```powershell
docker compose exec backend pytest -vv
```

Resultado apresentado:

| Resultado | Quantidade |
|---|---:|
| Testes aprovados | 148 |
| Testes com falha | 0 |
| Testes ignorados | 0 |
| Avisos | 1 |

Resumo do Pytest:

```text
148 passed, 1 warning
```

O aviso apresentado foi um `DeprecationWarning` relacionado ao `anyio.abc.BlockingPortal`, utilizado pela infraestrutura de testes do Starlette.

Não houve falhas na execução.

## 3. Testes do frontend

### Execução em 25/11/2026

Comando:

```powershell
docker compose exec -e CI=true frontend npm test -- --watchAll=false
```

Resultado apresentado:

| Resultado | Quantidade |
|---|---:|
| Testes aprovados | 10 |
| Testes com falha | 0 |

Os testes aprovados verificaram:

- Exibição do editor e do botão de análise.
- Seleção de exemplos.
- Validação de entrada vazia.
- Comunicação com o endpoint de análise.
- Exibição de tokens léxicos e estruturais.
- Exibição e seleção de nós da AST.
- Expansão e recolhimento da árvore.
- Exibição de erros sintáticos com linha e coluna.
- Diferenciação entre erros léxicos e sintáticos.
- Tratamento de falhas de comunicação com o backend.

## 4. Build de produção

### Execução em 25/11/2026

Comando:

```powershell
docker compose exec frontend npm run build
```

Resultado:

```text
Compiled successfully.

File sizes after gzip:

49.97 kB  build/static/js/main.52e6c03d.js
2.37 kB   build/static/css/main.7252c22d.css

The build folder is ready to be deployed.
```

**Resultado:** aprovado.

A aplicação React foi compilada com sucesso para produção.

## 5. Validação do Docker Compose

### Execução em 25/11/2026

Comando:

```powershell
docker compose config
```

Resultado: configuração apresentada sem erros.

Foram identificados os serviços:

- `backend`, com porta 8000