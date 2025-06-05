import { useState } from 'react';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');

  const handleBypass = async () => {
    try {
      const response = await fetch('http://localhost:8000/bypass', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: inputText })
      });

      const result = await response.json();
      setOutputText(result.result);
    } catch (error) {
      alert('Error contacting backend. Is your Python server running?');
      console.error(error);
    }
  };

  const saveToTxt = () => {
    const blob = new Blob([outputText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'evasive_text.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="App">
      <h1>AI Watermark Evasion Tool</h1>
      <p>Paste AI-generated text below:</p>

      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="Paste ChatGPT or AI-generated text here"
        rows={10}
        cols={80}
      />

      <br />
      <button onClick={handleBypass}>Bypass Detection</button>

      <h2>Output:</h2>
      <textarea
        value={outputText}
        readOnly
        rows={10}
        cols={80}
        placeholder="Modified text will appear here"
      />

      <br />
      <button onClick={saveToTxt}>Save as .txt</button>
    </div>
  );
}

export default App;