import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getMe } from "../services/api";
import Login from "../components/Login";
import Signup from "../components/Signup";
// import logo from "../assets/logo3.png";
import "../styles/Navbar.css";


const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 0);
    window.addEventListener("scroll", handleScroll);

    // try auto-login if token exists
    const token = localStorage.getItem("token");
    if (token) {
      getMe()
        .then((u) => {
          setUser(u);
          setIsLoggedIn(true);
        })
        .catch(() => {
          localStorage.removeItem("token");
          setIsLoggedIn(false);
        });
    }

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setUser(null);
    setShowDropdown(false);
  };

  return (
    <>
      <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
        <div className="navbar-container">
          {/* Logo */}
          <div className="navbar-logo">
            <Link to="/" onClick={() => { setIsOpen(false); window.scrollTo(0, 0); }}>
              {/* <img src={logo} alt="Logo" /> */}
              PDF Assistant
            </Link>
          </div>

          {/* Links */}
          <div className={`navbar-links ${isOpen ? "active" : ""}`}>
            {!isLoggedIn ? (
              <>
                <a href="#">About</a>
                <a href="#">Features</a>
                <span onClick={() => setShowLogin(true)} className="nav-link-btn">Login</span>
                <span onClick={() => setShowSignup(true)} className="nav-link-btn">Sign Up</span>
              </>
            ) : (
              <>
                <Link to="/home">Home</Link>
                <Link to="/history">History</Link>

                <div className="profile-container">
                  <div className="profile-icon" onClick={() => setShowDropdown(!showDropdown)}>
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt="Profile" className="avatar" />
                    ) : (
                      <span className="avatar-text">
                        {user?.name?.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>

                  {showDropdown && (
                    <div className="dropdown-menu">
                      <Link to="/profile" className="dropdown-item" onClick={() => setShowDropdown(false)}>
                        Profile Settings
                      </Link>
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
            {isOpen ? <span className="close-icon">✖</span> : (
              <>
                <div className="bar"></div>
                <div className="bar"></div>
                <div className="bar"></div>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Modals */}
      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <Login
              onClose={() => setShowLogin(false)}
              switchToSignup={() => { setShowLogin(false); setShowSignup(true); }}
              onLoginSuccess={(userData) => { setUser(userData); setIsLoggedIn(true); setShowLogin(false); }}
            />
          </div>
        </div>
      )}

      {showSignup && (
        <div className="modal-overlay" onClick={() => setShowSignup(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <Signup
              onClose={() => setShowSignup(false)}
              switchToLogin={() => { setShowSignup(false); setShowLogin(true); }}
              onSignupSuccess={(userData) => { setUser(userData); setIsLoggedIn(true); setShowSignup(false); }}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
