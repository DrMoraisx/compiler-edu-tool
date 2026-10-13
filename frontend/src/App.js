import React, { useEffect, useState } from 'react';

function App() {
  const [backendMessage, setBackendMessage] = useState('A carregar...');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then((res) => res.json())
      .then((data) => setBackendMessage(data.message))
      .catch((err) => setBackendMessage('Erro ao conectar com o backend.'));
  }, []);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', textAlign: 'center', marginTop: '50px' }}>
      <h1>Compiler Edu Tool</h1>
      <p>Analisador Léxico Operacional</p>
      <div style={{ marginTop: '20px', padding: '15px', background: '#f0f0f0', display: 'inline-block', borderRadius: '5px' }}>
        <strong>Resposta do Backend:</strong> {backendMessage}
      </div>
    </div>
  );
}

export default App;