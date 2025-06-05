import React, { useState } from 'react';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState('');

  const handleBypass = async () => {
    const response = await fetch('http://127.0.0.1:8000/bypass', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    setResult(data.result);
  };

  const handleDownload = async () => {
    const response = await fetch('http://127.0.0.1:8000/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'watermarked_output.txt';
    a.click();
  };

  return (
    <div>
      <h1>Watermark Evasion Tool</h1>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text here..."
        rows="10"
        cols="50"
      />
      <br />
      <button onClick={handleBypass}>Bypass Watermark</button>
      <button onClick={handleDownload}>Download Watermarked File</button>
      <pre>{result}</pre>
    </div>
  );
}

export default App;
