import { useState } from 'react'
import './App.css'

function App() {
  const [inputText, setInputText] = useState("");
  const [response, setResponse] = useState("");

  async function sendMessage() {
    try {
      // 1. Send the POST request
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // We wrap our data in JSON.stringify
        body: JSON.stringify({ message: inputText }), 
      });

      // 2. Get the reply
      const data = await res.json();
      setResponse(data.reply);
      
    } catch (error) {
      console.log(error);
      setResponse("Error connecting to server.");
    }
  }

  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'Arial' }}>
      <h1>The Chat Bridge</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input 
          type="text" 
          placeholder="Type something here..." 
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          style={{ padding: '10px', width: '300px', fontSize: '16px' }}
        />
        <button 
          onClick={sendMessage}
          style={{ padding: '10px 20px', fontSize: '16px', marginLeft: '10px', cursor: 'pointer' }}
        >
          Send
        </button>
      </div>

      <h3>Server Reply:</h3>
      <p style={{ color: 'blue', fontWeight: 'bold' }}>{response}</p>
    </div>
  )
}

export default App