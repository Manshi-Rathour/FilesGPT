import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./App.css";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import ChatHistoryPage from "./components/ChatHistoryPage";
import LoadingUserPage from "./components/LoadingUserPage";

import LandingPage from "./pages/LandingPage";
import HowToUsePage from "./pages/HowToUsePage";
import AboutUsPage from "./pages/AboutUsPage";
import Home from "./pages/Home";
import PDFPage from "./pages/PDFPage";
import ImagePage from "./pages/ImagePage";
import WebsitePage from "./pages/WebsitePage";
import ChatPage from "./pages/ChatPage";
import ProfileSettings from "./pages/ProfileSettings";

function App() {
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loadingUser, setLoadingUser] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setIsLoggedIn(false);
      setLoadingUser(false);
    } else {
      // Show mediator page while fetching user
      setLoadingUser(false);
    }
  }, []);

  if (loadingUser) return <LoadingUserPage setUser={setUser} setIsLoggedIn={setIsLoggedIn} />;

  return (
    <div className="App">
      <Navbar
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        user={user}
        setUser={setUser}
      />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/how-to-use" element={<HowToUsePage />} />
        <Route path="/about-us" element={<AboutUsPage />} />

        {/* Mediator page */}
        <Route
          path="/user-loading"
          element={<LoadingUserPage setUser={setUser} setIsLoggedIn={setIsLoggedIn} />}
        />

        {/* Home with ProtectedRoute */}
        <Route
          path="/home"
          element={
            <ProtectedRoute isLoggedIn={isLoggedIn}>
              <Home user={user} />
            </ProtectedRoute>
          }
        />

        <Route
          path="/pdf"
          element={<ProtectedRoute isLoggedIn={isLoggedIn}><PDFPage /></ProtectedRoute>}
        />
        <Route
          path="/image"
          element={<ProtectedRoute isLoggedIn={isLoggedIn}><ImagePage /></ProtectedRoute>}
        />
        <Route
          path="/website"
          element={<ProtectedRoute isLoggedIn={isLoggedIn}><WebsitePage /></ProtectedRoute>}
        />
        <Route
          path="/chat"
          element={<ProtectedRoute isLoggedIn={isLoggedIn}><ChatPage /></ProtectedRoute>}
        />
        <Route
          path="/profile"
          element={<ProtectedRoute isLoggedIn={isLoggedIn}><ProfileSettings /></ProtectedRoute>}
        />
        <Route
          path="/chat-history/:chatId"
          element={<ProtectedRoute isLoggedIn={isLoggedIn}><ChatHistoryPage /></ProtectedRoute>}
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;
