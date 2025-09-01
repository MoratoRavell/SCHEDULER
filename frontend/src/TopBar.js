// TopBar.js
import React, { useEffect, useState } from "react";

// COMPONENTS
import LoginModal from "./LoginModal";
import SignupModal from "./SignupModal";
import LogoutConfirmModal from "./LogoutConfirmModal";

// CSS
import './TopBar.css';

const TopBar = (props) => {
    const {
        onLoginSuccess,
        onLogout,
        isRunning,
        handleStopModel,
        setOutput,
        setIsContainerClickable,
        setResetUploader,
        logoutConfirmMessage,
        afterLogout,
        onHeaderClick,
        showHeaderAsClickable = false,
    } = props;

    const effectiveMessage = logoutConfirmMessage || "Are you sure you want to log out?";

    const [loggedInUserId, setLoggedInUserId] = useState(() => sessionStorage.getItem("user_id") || null);
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [showSignupModal, setShowSignupModal] = useState(false);
    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
    const [isHoveredLogin, setIsHoveredLogin] = useState(false);
    const [isHoveredSignup, setIsHoveredSignup] = useState(false);

    const handleAuthSuccess = (user_id) => {
        setLoggedInUserId(user_id);
        sessionStorage.setItem("user_id", user_id);
        onLoginSuccess?.(user_id);
    };

    const handleLogoutClick = async () => {
        // API CALL (auth.py)
        await fetch("http://localhost:8000/logout", { method: "POST", credentials: "include" });

        if (isRunning === true) {
            await handleStopModel();
        }

        sessionStorage.removeItem("user_id");
        setLoggedInUserId(null);
        setShowLogoutConfirm(false);
        setOutput?.("");
        setIsContainerClickable?.(false);
        setResetUploader?.(prev => !prev);
        onLogout?.();
        afterLogout?.();
    };

    useEffect(() => {
        const savedUserId = sessionStorage.getItem("user_id");
        if (savedUserId) setLoggedInUserId(savedUserId);
    }, []);

    return (
        <>
            <div
                style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: "60px",
                    backgroundColor: "#fff",
                    borderBottom: "1px solid #ccc",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0 20px",
                    zIndex: 100,
                }}
            >
                <div
                    className={`header ${showHeaderAsClickable ? "clickable-header" : ""}`}
                    onClick={showHeaderAsClickable ? onHeaderClick : undefined}
                    >
                    SCHEDULER
                </div>
                <div>
                    <button
                        onClick={() => loggedInUserId ? setShowLogoutConfirm(true) : setShowLoginModal(true)}
                        onMouseEnter={() => !loggedInUserId && setIsHoveredLogin(true)}
                        onMouseLeave={() => !loggedInUserId && setIsHoveredLogin(false)}
                        style={{
                            padding: "10px 20px",
                            fontSize: "16px",
                            backgroundColor: "transparent",
                            border: "none",
                            cursor: "pointer",
                            color: isHoveredLogin && !loggedInUserId ? "#007bff" : "black",
                            transition: "color 0.2s ease-in-out",
                        }}
                    >
                        {loggedInUserId ? "Log Out" : "Log In"}
                    </button>

                    <button
                        onClick={() => setShowSignupModal(true)}
                        disabled={!!loggedInUserId}
                        onMouseEnter={() => !loggedInUserId && setIsHoveredSignup(true)}
                        onMouseLeave={() => !loggedInUserId && setIsHoveredSignup(false)}
                        style={{
                            padding: "10px 20px",
                            fontSize: "16px",
                            backgroundColor: "transparent",
                            border: "none",
                            cursor: loggedInUserId ? "not-allowed" : "pointer",
                            opacity: loggedInUserId ? 0.5 : 1,
                            color: isHoveredSignup && !loggedInUserId ? "#007bff" : "black",
                            transition: "color 0.2s ease-in-out",
                        }}
                    >
                        Sign Up
                    </button>
                </div>
            </div>

            {showLoginModal && (
                <LoginModal
                    onClose={() => setShowLoginModal(false)}
                    onSuccess={handleAuthSuccess}
                />
            )}

            {showSignupModal && (
                <SignupModal
                    onClose={() => setShowSignupModal(false)}
                    onSuccess={handleAuthSuccess}
                />
            )}

            {showLogoutConfirm && (
                <LogoutConfirmModal
                    onClose={() => setShowLogoutConfirm(false)}
                    onConfirm={handleLogoutClick}
                    message={effectiveMessage }
                />
            )}
        </>
    );
};

export default TopBar;
