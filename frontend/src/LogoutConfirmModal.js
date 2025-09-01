// src/components/LogoutConfirmModal.js
import React, { useEffect } from 'react';

// CSS
import './LoginSignupModal.css';

const LogoutConfirmModal = ({ onClose, onConfirm, message = "Are you sure you want to log out?" }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'Enter') {
        onConfirm();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, onConfirm]);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Confirm Logout</h2>
        <p>{message}</p>
        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button className="logout-button" onClick={onConfirm}>Log Out</button>
        </div>
      </div>
    </div>
  );
};

export default LogoutConfirmModal;
