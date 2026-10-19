import React, { useState } from 'react';

function App() {
  const [code, setCode] = useState('# Exemplo em Mini-Python\nx = 10\ny = 20\nprint(x + y)');
  const [result, setResult] = useState(null);
  const [astResult, setAstResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/lexical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const data = await response.json();
      setResult(data);
      
      const parseResponse = await fetch('http://127.0.0.1:8000/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const parseData = await parseResponse.json();
      setAstResult(parseData);
    } catch (err) {
      alert('Erro ao conectar com o backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '30px auto', fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Compiler Edu Tool</h1>
      <p>Analisador Léxico e Sintático - Subconjunto Mini-Python</p>

      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '5px' }}>Código Fonte:</label>
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
        {loading ? 'A processar...' : 'Executar Compilação (Léxico + Sintático)'}
      </button>

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
          <h2>Árvore Sintática Abstrata (AST / Parser)</h2>
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