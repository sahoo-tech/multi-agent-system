import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [jsonBody, setJsonBody] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else if (jsonBody.trim()) {
      formData.append('json_body', jsonBody);
    } else if (emailBody.trim()) {
      formData.append('email_body', emailBody);
    } else {
      alert('Please provide a file, JSON body, or email body.');
      setLoading(false);
      return;
    }

    try {
      console.log('Sending request to backend...');
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const response = await axios.post(`${apiUrl}/intake/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 10000, // 10 second timeout
      });
      
      console.log('Response status:', response.status);
      console.log('Response data:', response.data);
      setResult(response.data);
    } catch (error) {
      console.error('Axios error:', error);
      if (error.response) {
        // Server responded with error status
        alert(`Server error: ${error.response.status} - ${error.response.data}`);
        setResult({ error: `Server error: ${error.response.status}` });
      } else if (error.request) {
        // Request was made but no response received
        alert('Network error: No response from server');
        setResult({ error: 'Network error: No response from server' });
      } else {
        // Something else happened
        alert('Error: ' + error.message);
        setResult({ error: error.message });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 20 }}>
      <h1>Multi-Agent Input Processor</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Upload PDF File:</label><br />
          <input type="file" accept="application/pdf" onChange={handleFileChange} />
        </div>
        <div style={{ marginTop: 10 }}>
          <label>Or enter JSON Body:</label><br />
          <textarea
            rows={6}
            style={{ width: '100%' }}
            value={jsonBody}
            onChange={(e) => setJsonBody(e.target.value)}
            placeholder='{"id": "123", "type": "example", "attributes": {}}'
          />
        </div>
        <div style={{ marginTop: 10 }}>
          <label>Or enter Email Body:</label><br />
          <textarea
            rows={6}
            style={{ width: '100%' }}
            value={emailBody}
            onChange={(e) => setEmailBody(e.target.value)}
            placeholder='From: John Doe <john@example.com>\nSubject: Complaint about service...'
          />
        </div>
        <button type="submit" disabled={loading} style={{ marginTop: 10 }}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 20 }}>
          <h2>Result</h2>
          <pre style={{ backgroundColor: '#f0f0f0', padding: 10, whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
