import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Login from "../components/Login";
import Signup from "../components/Signup";
import "../styles/Navbar.css";

const Navbar = ({ isLoggedIn, setIsLoggedIn, user, setUser }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setUser(null);
    setShowDropdown(false);
    navigate("/"); // redirect to landing page
  };

  return (
    <>
      <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
        <div className="navbar-container">
          {/* Logo */}
          <div className="navbar-logo">
            <Link to="/" onClick={() => setIsOpen(false)}>FilesGPT</Link>
          </div>

          {/* Links */}
          <div className={`navbar-links ${isOpen ? "active" : ""}`}>
            {!isLoggedIn ? (
              <>
                <Link to="/about-us" onClick={() => setIsOpen(false)}>About</Link>
                <Link to="/how-to-use" onClick={() => setIsOpen(false)}>How To Use</Link>
                <span onClick={() => setShowLogin(true)} className="nav-link-btn">Login</span>
                <span onClick={() => setShowSignup(true)} className="nav-link-btn">Sign Up</span>
              </>
            ) : (
              <>
                <Link to="/home" onClick={() => setIsOpen(false)}>Home</Link>
                <div className="profile-container">
                  <div className="profile-icon" onClick={() => setShowDropdown(!showDropdown)}>
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt="Profile" className="avatar" />
                    ) : (
                      <span className="avatar-text">{user?.name?.charAt(0).toUpperCase()}</span>
                    )}
                  </div>

                  {showDropdown && (
                    <div className="dropdown-menu">
                      <span className="dropdown-item" onClick={() => { navigate("/profile"); setShowDropdown(false); }}>
                        Profile Settings
                      </span>
                      <span className="dropdown-item" onClick={handleLogout}>
                        Sign Out
                      </span>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Hamburger */}
          <div className="menu-toggle" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <span className="close-icon">✖</span> : <>
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
            </>}
          </div>
        </div>
      </nav>

      {/* Modals */}
      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <Login
              onClose={() => setShowLogin(false)}
              switchToSignup={() => { setShowLogin(false); setShowSignup(true); }}
              onLoginSuccess={(userData) => { setUser(userData); setIsLoggedIn(true); setShowLogin(false); navigate("/home"); }}
            />
          </div>
        </div>
      )}

      {showSignup && (
        <div className="modal-overlay" onClick={() => setShowSignup(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <Signup
              onClose={() => setShowSignup(false)}
              switchToLogin={() => { setShowSignup(false); setShowLogin(true); }}
              onSignupSuccess={(userData) => { setUser(userData); setIsLoggedIn(true); setShowSignup(false); navigate("/home"); }}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
