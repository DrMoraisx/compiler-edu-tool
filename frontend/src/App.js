import React, { useState } from 'react';

const EXEMPLES = {
  ex1: `# Exemplo 1: Atribuição e Print\nx = 10\ny = 20\nprint(x + y)`,
  ex2: `# Exemplo 2: Estrutura Condicional (If)\nx = 15\nif x > 10:\n    print(x)`,
  ex3: `# Exemplo 3: Definição de Função\ndef soma(a, b):\n    return a + b`
};

function App() {
  const [code, setCode] = useState(EXEMPLES.ex1);
  const [result, setResult] = useState(null);
  const [astResult, setAstResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSelectExample = (e) => {
    const key = e.target.value;
    if (EXEMPLES[key]) {
      setCode(EXEMPLES[key]);
      setErrorMsg(null);
    }
  };

  const handleAnalyze = async () => {
    setErrorMsg(null);
    setResult(null);
    setAstResult(null);

    if (!code.trim()) {
      setErrorMsg("Informe um código-fonte antes de solicitar a análise.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/lexical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error("Falha na comunicação com o servidor backend.");
      }

      const data = await response.json();
      setResult(data);
      
      const parseResponse = await fetch('http://127.0.0.1:8000/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      if (parseResponse.ok) {
        const parseData = await parseResponse.json();
        setAstResult(parseData);
      }
    } catch (err) {
      setErrorMsg("Não foi possível comunicar com o servidor. Verifique a conexão e tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '30px auto', fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Compiler Edu Tool</h1>
      <p><strong>Linguagem Analisada:</strong> Subconjunto Mini-Python</p>

      <div style={{ marginBottom: '15px' }}>
        <label style={{ fontWeight: 'bold', marginRight: '10px' }}>Carregar Exemplo:</label>
        <select onChange={handleSelectExample} style={{ padding: '5px 10px', fontSize: '14px' }}>
          <option value="ex1">Exemplo 1 — Atribuição e Operação</option>
          <option value="ex2">Exemplo 2 — Condicional (if)</option>
          <option value="ex3">Exemplo 3 — Definição de Função (def)</option>
        </select>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '5px' }}>Área de Entrada do Código-Fonte:</label>
        <textarea
          rows="8"
          style={{ width: '100%', padding: '10px', fontFamily: 'monospace', fontSize: '14px' }}
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </div>

      <button
        onClick={handleAnalyze}
        style={{ padding: '10px 20px', background: '#007bff', color: '#fff', border: 'none', cursor: 'pointer', borderRadius: '4px', fontSize: '16px' }}
      >
        {loading ? 'A processar...' : 'Executar Análise do Código'}
      </button>

      {errorMsg && (
        <div style={{ marginTop: '20px', background: '#f8d7da', color: '#721c24', padding: '12px', borderRadius: '4px', border: '1px solid #f5c6cb' }}>
          <strong>Aviso:</strong> {errorMsg}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '30px' }}>
          <h2>Resultados da Análise Léxica</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Tipo</th>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Lexema</th>
                <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #dee2e6' }}>Linha</th>
              </tr>
            </thead>
            <tbody>
              {result.tokens.map((token, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', color: '#0056b3', fontWeight: 'bold' }}>{token.type}</td>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', fontFamily: 'monospace' }}>{token.value}</td>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>{token.line}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {astResult && (
        <div style={{ marginTop: '30px' }}>
          <h2>Árvore Sintática Abstrata (AST)</h2>
          {astResult.error ? (
            <div style={{ background: '#ffe6e6', padding: '10px', borderLeft: '5px solid red' }}>
              <strong>Erro Sintático:</strong> {astResult.error}
            </div>
          ) : (
            <pre style={{ background: '#f4f4f4', padding: '15px', borderRadius: '5px', overflowX: 'auto', fontFamily: 'monospace' }}>
              {JSON.stringify(astResult.ast, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export default App;