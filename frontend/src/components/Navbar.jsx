import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getMe } from "../services/api";
import Login from "../components/Login";
import Signup from "../components/Signup";
import "../styles/Navbar.css";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 0);
    window.addEventListener("scroll", handleScroll);

    const token = localStorage.getItem("token");
    if (token) {
      getMe()
        .then((u) => {
          setUser(u);
          setIsLoggedIn(true);

          // Redirect only if on landing/login/signup pages
          if (
            window.location.pathname === "/" ||
            window.location.pathname === "/login" ||
            window.location.pathname === "/signup"
          ) {
            navigate("/home");
          }
        })
        .catch(() => {
          localStorage.removeItem("token");
          setIsLoggedIn(false);
        });
    }

    return () => window.removeEventListener("scroll", handleScroll);
  }, [navigate]);

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
            <Link
              to="/"
              onClick={() => {
                setIsOpen(false);
                window.scrollTo(0, 0);
              }}
            >
              FilesGPT
            </Link>
          </div>

          {/* Links */}
          <div className={`navbar-links ${isOpen ? "active" : ""}`}>
            {!isLoggedIn ? (
              <>
                <Link to="/about-us">About</Link>
                <Link to="/features">Features</Link>
                <Link to="/how-to-use">How To Use</Link>
                <span
                  onClick={() => setShowLogin(true)}
                  className="nav-link-btn"
                >
                  Login
                </span>
                <span
                  onClick={() => setShowSignup(true)}
                  className="nav-link-btn"
                >
                  Sign Up
                </span>
              </>
            ) : (
              <>
                <Link to="/home">Home</Link>

                <div className="profile-container">
                  <div
                    className="profile-icon"
                    onClick={() => setShowDropdown(!showDropdown)}
                  >
                    {user?.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt="Profile"
                        className="avatar"
                      />
                    ) : (
                      <span className="avatar-text">
                        {user?.name?.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>

                  {showDropdown && (
                    <div className="dropdown-menu">
                      <span
                        className="dropdown-item"
                        onClick={() => {
                          navigate("/profile"); // navigate first
                          setShowDropdown(false); // close dropdown after
                        }}
                      >
                        Profile Settings
                      </span>
                      <span
                        className="dropdown-item"
                        onClick={handleLogout}
                      >
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
            {isOpen ? (
              <span className="close-icon">✖</span>
            ) : (
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
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <Login
              onClose={() => setShowLogin(false)}
              switchToSignup={() => {
                setShowLogin(false);
                setShowSignup(true);
              }}
              onLoginSuccess={(userData) => {
                setUser(userData);
                setIsLoggedIn(true);
                setShowLogin(false);
                navigate("/home"); // redirect after login
              }}
            />
          </div>
        </div>
      )}

      {showSignup && (
        <div className="modal-overlay" onClick={() => setShowSignup(false)}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <Signup
              onClose={() => setShowSignup(false)}
              switchToLogin={() => {
                setShowSignup(false);
                setShowLogin(true);
              }}
              onSignupSuccess={(userData) => {
                setUser(userData);
                setIsLoggedIn(true);
                setShowSignup(false);
                navigate("/home"); // redirect after signup
              }}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
