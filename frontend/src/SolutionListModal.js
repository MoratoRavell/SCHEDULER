import React, { useEffect, useState } from "react";

// CSS
import "./SolutionListModal.css";

// API CALLS
import {
  fetchSolutionsList,
  deleteSolution,
} from './APIcalls';

export default function SolutionListModal({ isOpen, onClose, onLoadSolution, userID }) {
  const [solutions, setSolutions] = useState([]);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  useEffect(() => {
    if (isOpen) {
      // API call
      fetchSolutionsList(userID)
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        console.log("Received from API:", data);
        if (Array.isArray(data)) setSolutions(data);
        else {
          console.error("Expected array, got:", data);
          setSolutions([]);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch solutions", err);
        setSolutions([]);
      });
    }
    setConfirmDeleteId(null)
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (confirmDeleteId && e.key === "Enter") {
        e.preventDefault();
        handleDelete(confirmDeleteId);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [confirmDeleteId]);

  const handleDelete = (solutionId) => {
    // API call
    deleteSolution(userID, solutionId)
        .then(() => {
          setSolutions((prev) => prev.filter((s) => s !== solutionId));
          setConfirmDeleteId(null);
        })
        .catch((err) => {
          console.error("Failed to delete solution", err);
        });
    };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal">
        <h2 className="modal-title">Load a Solution</h2>
        <div className="solution-list">
          {solutions.map((solutionId) => (
            <div key={solutionId} className="solution-item">
              <span
                className="solution-id"
                onClick={() => {
                  onLoadSolution(solutionId);
                  onClose();
                }}
              >
                {solutionId}
              </span>
              <button
                className="x-delete-button"
                onClick={() => setConfirmDeleteId(solutionId)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </div>

      {confirmDeleteId && (
        <>
          <div className="modal-overlay" onClick={() => setConfirmDeleteId(null)} />
            <div className="confirm-modal">
            <h3>Delete this solution?</h3>
            <p>
                Are you sure you want to delete <strong>{confirmDeleteId}</strong>?
            </p>
            <div className="confirm-buttons">
              <button
                className="modal-button cancel-button"
                onClick={() => setConfirmDeleteId(null)}
              >
                Cancel
              </button>
              <button
                className="modal-button delete-button"
                onClick={() => handleDelete(confirmDeleteId)}
              >
                Delete
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
}
