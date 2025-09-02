import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { WalkthroughProvider } from "./contexts/WalkthroughContext";
import LoginSignup from "./components/LoginSignup";
import Dashboard from "./components/Dashboard";
import WalkthroughOverlay from "./components/WalkthroughOverlay";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <ThemeProvider>
      <WalkthroughProvider>
        <div className="App min-h-screen bg-background text-foreground transition-colors duration-300">
          <BrowserRouter>
            <Routes>
              <Route 
                path="/login" 
                element={
                  isAuthenticated ? 
                  <Navigate to="/dashboard" replace /> : 
                  <LoginSignup setIsAuthenticated={setIsAuthenticated} />
                } 
              />
              <Route 
                path="/dashboard" 
                element={
                  isAuthenticated ? 
                  <Dashboard setIsAuthenticated={setIsAuthenticated} /> : 
                  <Navigate to="/login" replace />
                } 
              />
              <Route path="/" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
          <WalkthroughOverlay />
        </div>
      </WalkthroughProvider>
    </ThemeProvider>
  );
}

export default App;