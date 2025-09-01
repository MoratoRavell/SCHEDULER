import React, { useState, useRef, useEffect } from "react";

// CSS
import "./SaveModal.css";

export default function SaveModal({ isOpen, onClose, onSave }) {
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState("");
  const modalRef = useRef(null);

  const isValidSQLIdentifier = (value) => {
  if (value.trim() === "") return false;
  if (value.length > 63) return false;
  if (value.toLowerCase() === "temp_sol") return false;  // reserved for the temp solution, to avoid requiring additional tables
  return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(value);
};

  useEffect(() => {
    if (isOpen) {
      setInputValue("");
      setError("");
    }
  }, [isOpen]);

  const saveName = () => {
    if (!isValidSQLIdentifier(inputValue)) {
      setError(
        "Invalid name. Must start with a letter or underscore and contain only letters, digits, or underscores. Max 63 characters."
      );
      return;
    }
    onSave(inputValue);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      } else if (event.key === "Enter") {
        saveName();
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, inputValue]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal" ref={modalRef}>
        <h2 className="modal-title">Enter a name</h2>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setError("");
          }}
          className="modal-input"
          autoFocus
        />
        {error && <p className="error-text">{error}</p>}
        <div className="modal-buttons">
          <button onClick={onClose} className="cancel-button">
            Cancel
          </button>
          <button
            onClick={saveName}
            className="save-button"
            disabled={!isValidSQLIdentifier(inputValue)}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
