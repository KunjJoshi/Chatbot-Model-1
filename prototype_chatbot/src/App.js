import React, { useState } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  const handleSendMessage = async () => {
    if (userInput.trim() !== '') {
      const uid = uuidv4(); // Generate a unique ID for each user message
      const userMessage = { role: 'user', content: userInput, uid }; // Include the uid in the user message
      setMessages((prevMessages) => [...prevMessages, userMessage]);

      try {
        const response = await axios.post('/get_response', { user_query: userInput, uid }); // Send the uid to the backend
        const chatbotResponse = response.data.response;
        const chatbotMessages = chatbotResponse.split('\n').map((paragraph) => ({
          role: 'chatbot',
          content: paragraph,
          uid, // Use the same uid for chatbot response
        }));
        setMessages((prevMessages) => [...prevMessages, ...chatbotMessages]);
      } catch (error) {
        console.error('Error fetching response from backend:', error);
      }

      setUserInput('');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>ChatBot App</h1>
      </header>
      <div className="chat-container">
        <div className="message-list">
          {messages.map((message) => (
            <div className={`message ${message.role}`} key={message.uid}>
              {message.content}
            </div>
          ))}
        </div>
        <div className="message-box">
          <input
            type="text"
            placeholder="Type your message here..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSendMessage();
              }
            }}
          />
          <button className="send-button" onClick={handleSendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
