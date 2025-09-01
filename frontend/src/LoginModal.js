import React, { useState, useEffect } from 'react';

// CSS
import './LoginSignupModal.css';

const LoginModal = ({ onClose, onSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const isValidInput = (value) => value.trim() !== '' && !/\s/.test(value);
  const validateInputs = () => isValidInput(username) && isValidInput(password);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'Enter') {
        if (validateInputs()) {
          submit();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [username, password, onClose]);

  const submit = async () => {
    setLoading(true);
    try {
      // API CALL (auth.py)
      const response = await fetch(`http://localhost:8000/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      onSuccess(data.user_id);
      onClose();
    } catch (err) {
      alert(err.message || "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="login-modal" onClick={e => e.stopPropagation()}>
        <h2>Log In</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          disabled={loading}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          disabled={loading}
        />

        <div className="modal-actions">
          <button onClick={onClose} disabled={loading}>Cancel</button>
          <button onClick={submit} disabled={!validateInputs() || loading}>
            {loading ? "Loading..." : "Accept"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
