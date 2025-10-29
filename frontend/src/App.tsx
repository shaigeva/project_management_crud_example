import { useState, useEffect } from 'react';
import apiClient from './services/api';
import './index.css';

function App() {
  const [healthStatus, setHealthStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading');
  const [message, setMessage] = useState('Checking connection...');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await apiClient.getHealth();
        if (response.status === 'ok') {
          setHealthStatus('connected');
          setMessage('✓ Connected to backend');
        } else {
          setHealthStatus('disconnected');
          setMessage(`✗ Backend returned: ${response.status}`);
        }
      } catch (error) {
        setHealthStatus('disconnected');
        if (error instanceof Error) {
          setMessage(`✗ Failed to connect: ${error.message}`);
        } else {
          setMessage('✗ Failed to connect to backend');
        }
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="App">
      <h1>Project Management System</h1>
      <div className="card">
        <p>Hello World from Project Management App</p>
        <p style={{ fontSize: '0.9em', color: '#888' }}>
          Frontend running on port 3000
        </p>
      </div>
      <div className={`status ${healthStatus}`}>
        <strong>Backend Status:</strong> {message}
      </div>
    </div>
  );
}

export default App;
