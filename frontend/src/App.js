import React, { useState } from 'react';

function App() {
  const [code, setCode] = useState('# Exemplo em Mini-Python\nx = 10\ny = 20\nresultado = x + y\nprint(resultado)');
  const [result, setResult] = useState(null);
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
    } catch (err) {
      alert('Erro ao conectar com o backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '30px auto', fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Compiler Edu Tool</h1>
      <p>Analisador Léxico - Subconjunto Mini-Python</p>

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
        {loading ? 'A analisar...' : 'Executar Análise Léxica'}
      </button>

      {result && (
        <div style={{ marginTop: '30px' }}>
          <h2>Resultados da Análise Léxica</h2>
          
          {result.errors.length > 0 && (
            <div style={{ background: '#ffe6e6', padding: '10px', marginBottom: '15px', borderLeft: '5px solid red' }}>
              <h3>Erros Léxicos Encontrados:</h3>
              <ul>
                {result.errors.map((err, idx) => (
                  <li key={idx}>Linha {err.line}, Coluna {err.column}: {err.error}</li>
                ))}
              </ul>
            </div>
          )}

          <h3>Tokens Reconhecidos ({result.tokens.length}):</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Tipo do Token</th>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Lexema (Valor)</th>
                <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #dee2e6' }}>Linha</th>
                <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #dee2e6' }}>Coluna</th>
              </tr>
            </thead>
            <tbody>
              {result.tokens.map((token, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', color: '#0056b3', fontWeight: 'bold' }}>{token.type}</td>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', fontFamily: 'monospace' }}>{token.value}</td>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>{token.line}</td>
                  <td style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>{token.column}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;