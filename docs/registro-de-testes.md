# Registro de Testes

Este arquivo registra as execuções relevantes dos testes automatizados.
Os comandos podem ser reproduzidos conforme a seção 9 do README.

## Estratégia

| Tipo | Arquivo | Ferramenta | O que verifica |
|---|---|---|---|
| Unitário (scanner) | `backend/tests/test_lexer.py` | Pytest | Cada palavra reservada, identificadores, literais, operadores (simples e compostos), delimitadores, comentários, espaços, posição (linha/coluna), erros léxicos acumulados, casos de borda |
| Unitário (prévia do parser) | `backend/tests/test_parser.py` | Pytest | AST, precedência, blocos, erros sintáticos com linha |
| Endpoints / validações | `backend/tests/test_main.py` | Pytest + TestClient | Contrato (`sucesso`, `tokens`, `erros`), códigos HTTP, entrada vazia, só espaços, payload inválido, JSON malformado, erro inesperado, CORS |
| Implantação | `backend/tests/test_deploy.py` | Pytest + urllib | Serviços reais no ar: `/health`, `/api/parse`, página do frontend |
| Interface | `frontend/src/App.test.js` | Jest + React Testing Library | Tela, edição, exemplos, envio, tabela de tokens, erros, código colorido, passo a passo, tutorial, mensagens de validação e de falha de comunicação |
| Regressão | todos os acima | — | Os testes das Etapas 1 e 2 permanecem no conjunto e são reexecutados a cada alteração |

## Execução de 23/10/2026 (ambiente de desenvolvimento)

| Módulo | Comando | Aprovados | Reprovados | Ignorados |
|---|---|---|---|---|
| Backend (scanner + parser + endpoints) | `python -m pytest` | 178 | 0 | 6 (implantação, serviços fora do ar) |
| Backend (implantação, backend no ar) | `python -m pytest tests/test_deploy.py` | 5 | 0 | 1 (frontend não acessível nesse ambiente) |
| Frontend (interface) | `CI=true npx react-scripts test --watchAll=false` | 57 | 0 | 0 |
| Frontend (build de produção) | `npx react-scripts build` | compilou sem erros | — | — |

Observações:
* O frontend foi executado 3 vezes seguidas para verificar estabilidade: 57/57 em todas.
* Nesse ambiente o Docker não estava disponível. O `docker-compose.yml` (com `healthcheck`) teve a sintaxe YAML validada, mas **a subida dos contêineres deve ser conferida com os comandos do README**.

## Execução no Docker Compose (preencher após rodar)

| Data | Comando | Aprovados | Reprovados | Observações |
|---|---|---|---|---|
|  | `docker compose exec backend python -m pytest -v` |  |  |  |
|  | `docker compose exec backend python -m pytest tests/test_deploy.py -v` |  |  |  |
|  | `docker compose exec -e CI=true frontend npm test -- --watchAll=false` |  |  |  |

## Falhas encontradas e correções

| Falha | Causa | Correção |
|---|---|---|
| `ModuleNotFoundError: No module named 'main'` nos testes do backend | Importação `from main import app`, com o módulo em `app/main.py` | Importação alterada para `from app.main import app` |
| `/api/parse` respondia HTTP 422 ao payload `{"codigo": ...}` | Modelo aceitava apenas o campo `code` | Contrato passou a usar `codigo` (com `code` aceito por compatibilidade) |
| Rodapé do frontend exibia "3/3 PASSED" fixo | Texto estático, sem relação com a execução real | Removido; resultados ficam neste registro |
| O scanner parava no primeiro erro léxico | Implementação levantava exceção | Reescrito para acumular os erros e continuar a leitura |
| `sucesso: false` para código com tokens válidos e erro sintático | O endpoint misturava análise léxica e sintática | `/api/parse` passou a executar só o scanner; a sintaxe ficou em `/api/syntax` (prévia) |
| Build de produção falhava (`Definition for rule 'react-hooks/exhaustive-deps' was not found`) | Comentário `eslint-disable` referenciava uma regra ausente na configuração do projeto | Comentário removido e dependências do `useMemo` corrigidas |
| Vários testes de interface falharam na primeira execução | Erros nos próprios testes (falta de `render`, coluna errada num caso com emoji, contagem de tokens) | Testes corrigidos; o código da aplicação não foi alterado por isso |

## Limitações e testes pendentes

* Não há testes de ponta a ponta no navegador real (por exemplo, Cypress ou Playwright). A integração frontend ↔ backend é verificada com `fetch` simulado no frontend e com requisições reais nos testes de implantação.
* A análise sintática (Etapa 4) e a semântica (Etapa 5) ainda não têm testes de interface.