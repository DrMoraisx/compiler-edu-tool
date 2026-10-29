
import React, { useMemo, useState } from 'react';
import './App.css';

const examples = {
  1: {
    title: 'Variáveis',
    code: '# Declaração e inicialização\nnumero = 10\nnome = "Ana"'
  },
  2: {
    title: 'Aritmética',
    code: '# Operações aritméticas\na = 10\nb = 5\nresultado = a + b * 2'
  },
  3: {
    title: 'Condicional',
    code: '# Estrutura condicional\nnumero = 15\nif numero > 10:\n    print("Maior que 10")\nelse:\n    print("Menor ou igual a 10")'
  }
};

function App() {
  const [code, setCode] = useState(examples[1].code);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('results');

  const tokenCounts = useMemo(() => {
    const counts = {};

    (result?.tokens || []).forEach((token) => {
      counts[token.tipo] = (counts[token.tipo] || 0) + 1;
    });

    return counts;
  }, [result]);

  function handleExampleSelect(event) {
    const example = examples[event.target.value];

    if (!example) return;

    setCode(example.code);
    setResult({
      localMessage: `Exemplo "${example.title}" carregado.`,
      sucesso: true,
      tokens: [],
      erros: []
    });
  }

  async function handleAnalyze() {
    if (!code.trim()) {
      setResult({
        localMessage:
          'Informe um código-fonte antes de solicitar a análise.',
        sucesso: false,
        tokens: [],
        erros: []
      });
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code })
      });

      const data = await response.json();

      if (!response.ok) {
        setResult({
          localMessage:
            data.detail || 'Não foi possível processar a entrada.',
          sucesso: false,
          tokens: [],
          erros: []
        });
      } else {
        setResult(data);
      }
    } catch {
      setResult({
        localMessage:
          'Não foi possível comunicar com o servidor. ' +
          'Verifique se o backend está ativo e tente novamente.',
        sucesso: false,
        tokens: [],
        erros: []
      });
    } finally {
      setLoading(false);
    }
  }

  const shownMessage =
    result?.localMessage ||
    result?.mensagem ||
    'Insira um código e clique em "Analisar código" para visualizar os tokens.';

  return (
    <main className="compiler-container">
      <header className="compiler-header">
        <div className="logo-area">
          <div className="logo-icon" aria-hidden="true">
            🧠
          </div>

          <div>
            <h1>EDUTER_TOOL</h1>
            <span className="badge-lang">
              MINI-PYTHON • SCANNER LÉXICO
            </span>
          </div>
        </div>

        <p className="header-info">
          Software educacional de compiladores · Etapas 1, 2 e 3
        </p>
      </header>

      <section className="intro">
        <h2>Explore como o código é dividido em tokens</h2>
        <p>
          Escreva ou selecione um exemplo. O scanner identifica
          lexemas, categorias e posições sem executar o programa.
        </p>
      </section>

      <div className="compiler-grid">
        <section className="editor-panel">
          <div className="panel-toolbar">
            <label htmlFor="examples">
              ÁREA DE ENTRADA DE CÓDIGO
            </label>

            <select
              id="examples"
              aria-label="Selecionar exemplo"
              onChange={handleExampleSelect}
              defaultValue=""
            >
              <option value="" disabled>
                Selecionar exemplo…
              </option>
              <option value="1">1. Variáveis e literais</option>
              <option value="2">2. Operações aritméticas</option>
              <option value="3">3. Estrutura condicional</option>
            </select>
          </div>

          <div className="editor-body">
            <div className="line-numbers" aria-hidden="true">
              {code.split('\n').map((_, index) => (
                <span key={index}>{index + 1}</span>
              ))}
            </div>

            <textarea
              aria-label="Código-fonte"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              spellCheck="false"
            />
          </div>

          <div className="editor-footer">
            <span>
              {code.length} caracteres · {code.split('\n').length} linhas
            </span>

            <button
              className="btn-analyze"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? 'ANALISANDO…' : 'ANALISAR CÓDIGO →'}
            </button>
          </div>
        </section>

        <aside className="sidebar-panel">
          <section className="result-card">
            <div className="card-tabs">
              <button
                className={
                  activeTab === 'results' ? 'tab active' : 'tab'
                }
                onClick={() => setActiveTab('results')}
              >
                RESULTADOS
              </button>

              <button
                className={
                  activeTab === 'docs' ? 'tab active' : 'tab'
                }
                onClick={() => setActiveTab('docs')}
              >
                GUIA RÁPIDO
              </button>
            </div>

            {activeTab === 'results' ? (
              <div
                className={`status-box ${
                  result && !result.sucesso ? 'error' : 'success'
                }`}
                role="status"
              >
                <strong>
                  {!result
                    ? 'SISTEMA PRONTO'
                    : result.sucesso
                      ? 'ANÁLISE CONCLUÍDA'
                      : 'VERIFIQUE A ENTRADA'}
                </strong>

                <p>{shownMessage}</p>

                {result?.observacao && (
                  <p className="note">{result.observacao}</p>
                )}
              </div>
            ) : (
              <div className="docs-box">
                <h3>Como interpretar</h3>
                <p>
                  <b>Token:</b> unidade reconhecida pelo scanner.
                </p>
                <p>
                  <b>Lexema:</b> texto exato que originou o token.
                </p>
                <p>
                  <b>Linha/coluna:</b> posição inicial do lexema.
                </p>
                <p>
                  Comentários iniciados por <code>#</code> e espaços
                  em branco são ignorados.
                </p>
              </div>
            )}
          </section>

          {activeTab === 'results' && result && (
            <>
              <section className="info-card">
                <h3>
                  TOKENS IDENTIFICADOS
                  <span>{result.tokens?.length || 0}</span>
                </h3>

                {(result.tokens || []).length > 0 ? (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Tipo</th>
                          <th>Lexema</th>
                          <th>Linha</th>
                          <th>Coluna</th>
                        </tr>
                      </thead>

                      <tbody>
                        {result.tokens.map((token, index) => (
                          <tr
                            key={`${token.linha}-${token.coluna}-${index}`}
                          >
                            <td>
                              <span className="token-type">
                                {token.tipo}
                              </span>
                            </td>
                            <td><code>{token.lexema}</code></td>
                            <td>{token.linha}</td>
                            <td>{token.coluna}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="muted">
                    Nenhum token para exibir.
                  </p>
                )}

                <div className="counts">
                  {Object.entries(tokenCounts).map(([type, count]) => (
                    <span key={type}>
                      {type}: <b>{count}</b>
                    </span>
                  ))}
                </div>
              </section>

              <section className="info-card">
                <h3>
                  ERROS LÉXICOS
                  <span
                    className={
                      result.erros?.length ? 'error-count' : ''
                    }
                  >
                    {result.erros?.length || 0}
                  </span>
                </h3>

                {result.erros?.length ? (
                  <ul className="errors-list">
                    {result.erros.map((error, index) => (
                      <li key={index}>
                        <b>
                          Linha {error.linha}, coluna {error.coluna}:
                        </b>{' '}
                        {error.mensagem}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="muted">
                    Nenhum erro léxico encontrado.
                  </p>
                )}
              </section>
            </>
          )}

          <section className="info-card examples-info">
            <h3>EXEMPLOS DISPONÍVEIS</h3>
            <p>
              <b>1.</b> Identificadores, inteiros e strings.
            </p>
            <p>
              <b>2.</b> Operadores aritméticos e atribuição.
            </p>
            <p>
              <b>3.</b> Palavras reservadas e delimitadores.
            </p>
          </section>
        </aside>
      </div>

      <footer>
        Compiler Edu Tool · Mini-Python · A análise sintática e
        semântica serão abordadas em etapas futuras.
      </footer>
    </main>
  );
}

export default App;
