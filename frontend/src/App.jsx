import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

import Navbar from './components/Navbar';

import LandingPage from './pages/LandingPage';
import HowToUsePage from './pages/HowToUsePage';
import AboutUsPage from './pages/AboutUsPage';
import Home from './pages/Home';
import PDFPage from './pages/PDFPage';
import ImagePage from './pages/ImagePage';
import WebsitePage from './pages/WebsitePage';
import ChatPage from './pages/ChatPage';
import ProfileSettings from './pages/ProfileSettings';

function App() {
  return (
    <div className="App">
      <Navbar />
      <div style={{ marginTop: '80px' }}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/how-to-use" element={<HowToUsePage />} />
          <Route path="/about-us" element={<AboutUsPage />} />
          <Route path="/home" element={<Home />} />
          <Route path="/pdf" element={<PDFPage />} />
          <Route path="/image" element={<ImagePage />} />
          <Route path="/website" element={<WebsitePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/profile" element={<ProfileSettings />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
