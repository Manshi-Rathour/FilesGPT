import React, { useState } from "react";
import "../styles/Auth.css";
import { signup, login, getMe } from "../services/api";
import { useNavigate } from "react-router-dom";

const Signup = ({ onClose = () => {}, switchToLogin = () => {}, onSignupSuccess = () => {} }) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [avatar, setAvatar] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("email", email);
      formData.append("password", password);
      if (avatar) formData.append("avatar", avatar);

      await signup(formData);

      // Automatically login after signup
      const res = await login(email, password);
      localStorage.setItem("token", res.access_token); // <-- save token

      // Navigate to mediator page
      navigate("/user-loading");

      const userData = await getMe();
      onSignupSuccess(userData);

      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <div className="auth-box">
      <button type="button" className="close-btn" onClick={onClose}>✖</button>

      <h2>Create Account</h2>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <input type="text" placeholder="Enter your name" required value={name} onChange={(e) => setName(e.target.value)} />

        <label>Email</label>
        <input type="email" placeholder="Enter your email" required value={email} onChange={(e) => setEmail(e.target.value)} />

        <label>Password</label>
        <input type="password" placeholder="Enter your password" required value={password} onChange={(e) => setPassword(e.target.value)} />

        <label>Profile Picture (optional)</label>
        <input type="file" accept="image/*" onChange={(e) => setAvatar(e.target.files[0])} />

        <button type="submit" className="auth-btn">Create Account</button>
      </form>

      <p className="link">
        Already have an account?{" "}
        <span className="switch-link" onClick={switchToLogin}>
          Sign In
        </span>
      </p>
    </div>
  );
};

export default Signup;
