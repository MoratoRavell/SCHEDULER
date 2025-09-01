import React, { useState, useEffect, useRef } from 'react';

// CSS
import './LoginSignupModal.css';

const isStrongPassword = (password) => {
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /\d/.test(password)
  );
};

const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const isValidName = (name) => /^[A-Za-zÀ-ÿ'-]{2,}$/.test(name); // Basic name/surname check
const isValidInput = (value) => value.trim() !== '' && !/\s/.test(value);

const SignupModal = ({ onClose, onSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [loading, setLoading] = useState(false);
  const [usernameTaken, setUsernameTaken] = useState(false);
  const [checkingUsername, setCheckingUsername] = useState(false);
  const debounceTimeout = useRef(null);

  const passwordsMatch = password === repeatPassword;

  const validateInputs = () => {
    return (
      isValidInput(username) &&
      !usernameTaken &&
      !checkingUsername &&
      isStrongPassword(password) &&
      passwordsMatch &&
      isValidEmail(email) &&
      isValidName(name) &&
      isValidName(surname)
    );
  };

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
  }, [onClose, name, surname, email, username, password, repeatPassword, usernameTaken, checkingUsername]);

  useEffect(() => {
    if (!isValidInput(username)) return setUsernameTaken(false);

    setCheckingUsername(true);
    if (debounceTimeout.current) clearTimeout(debounceTimeout.current);

    debounceTimeout.current = setTimeout(async () => {
      try {
        const res = await fetch(`http://localhost:8000/check-username?username=${encodeURIComponent(username)}`);
        const data = await res.json();
        setUsernameTaken(data.exists);
      } catch {
        setUsernameTaken(false);
      } finally {
        setCheckingUsername(false);
      }
    }, 500);

    return () => {
      if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    };
  }, [username]);

  const submit = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          username,
          password,
          name,
          surname,
          email
        }),
      });

      if (!response.ok)
        throw new Error((await response.json()).detail || 'Signup failed');

      onClose();
      onSuccess?.();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
        <div className="signup-modal" onClick={e => e.stopPropagation()}>
        <h2>Sign Up</h2>

        <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={e => setName(e.target.value)}
        />
        <p className={name === '' ? "default-message" : isValidName(name) ? "valid-message" : "error-message"}>
            {name === '' ? 'Required' : isValidName(name) ? "Valid name" : "Invalid name"}
        </p>

        <input
            type="text"
            placeholder="Surname"
            value={surname}
            onChange={e => setSurname(e.target.value)}
        />
        <p className={surname === '' ? "default-message" : isValidName(surname) ? "valid-message" : "error-message"}>
            {surname === '' ? 'Required' : isValidName(surname) ? "Valid surname" : "Invalid surname"}
        </p>

        <input
            type="text"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
        />
        <p className={email === '' ? "default-message" : isValidEmail(email) ? "valid-message" : "error-message"}>
            {email === '' ? 'Required' : isValidEmail(email) ? "Valid email" : "Invalid email"}
        </p>

        <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            />
            <p className={
            username === '' 
                ? "default-message" 
                : usernameTaken 
                ? "error-message" 
                : isValidInput(username) 
                    ? "valid-message" 
                    : ""
            }>
            {username === '' 
                ? 'Required'
                : checkingUsername 
                ? "Checking..."
                : usernameTaken 
                    ? "Username is already taken"
                    : "Username is available"
            }
            </p>

        <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
        />
        <p className={password === '' ? "default-message" : isStrongPassword(password) ? "valid-message" : "error-message"}>
            {password === '' ? 'Required' : isStrongPassword(password) ? "Strong password" : "Weak password"}
        </p>

        <input
            type="password"
            placeholder="Repeat Password"
            value={repeatPassword}
            onChange={e => setRepeatPassword(e.target.value)}
        />
        <p className={repeatPassword === '' ? "default-message" : passwordsMatch ? "valid-message" : "error-message"}>
            {repeatPassword === '' ? 'Required' : passwordsMatch ? "Passwords match" : "Passwords do not match"}
        </p>

        <div className="modal-actions">
            <button onClick={onClose} disabled={loading}>Cancel</button>
            <button onClick={submit} disabled={!validateInputs() || loading}>
              {loading ? 'Loading...' : 'Accept'}
            </button>
        </div>
        </div>
    </div>
  );
};

export default SignupModal;
