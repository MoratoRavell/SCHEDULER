// src/components/ReturnHomeConfirmModal.js
import React, { useEffect } from 'react';

// CSS
import './LoginSignupModal.css';

const ReturnHomeConfirmModal = ({ onClose, onConfirm }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Enter') onConfirm();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, onConfirm]);

  return (
    <div className="modal-backdrop" onClick={onClose}>
        <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Unsaved Solution</h2>
            <p>
            If you leave now, the current solution will be permanently lost.
            Make sure to save it before returning to the main screen.
            </p>
            <div className="modal-actions">
            <button onClick={onClose}>Cancel</button>
            <button className="return-home-button" onClick={onConfirm}>Leave</button>
            </div>
        </div>
    </div>
  );
};

export default ReturnHomeConfirmModal;
