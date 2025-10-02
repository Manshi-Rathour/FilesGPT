import React, { useState } from "react";
import "../styles/Auth.css";
import { login, getMe } from "../services/api";
import { useNavigate } from "react-router-dom";

const Login = ({ onClose = () => {}, switchToSignup = () => {}, onLoginSuccess = () => {} }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await login(email, password);
      localStorage.setItem("token", res.access_token); // <-- save token

      // Navigate to mediator page
      navigate("/user-loading");

      // Optional: fetch user data immediately (can also be done in LoadingUserPage)
      const userData = await getMe();
      onLoginSuccess(userData);

      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="auth-box">
      <button type="button" className="close-btn" onClick={onClose}>✖</button>

      <h2>Sign In</h2>
      <p className="subtitle">Welcome back! Please sign in to your account.</p>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleSubmit}>
        <label>Email</label>
        <input type="email" placeholder="Enter your email" required value={email} onChange={(e) => setEmail(e.target.value)} />

        <label>Password</label>
        <input type="password" placeholder="Enter your password" required value={password} onChange={(e) => setPassword(e.target.value)} />

        <button type="submit" className="auth-btn">Sign In</button>
      </form>

      <p className="link">
        Don’t have an account?{" "}
        <span className="switch-link" onClick={switchToSignup}>
          Sign up
        </span>
      </p>

      <p className="link small"><a href="#">Forgot your password?</a></p>
    </div>
  );
};

export default Login;
