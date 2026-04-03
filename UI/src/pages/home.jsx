import React from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

const Home = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login"); 
  };

  return (
    <div className="home-container">
      <div className="overlay">
        <div className="home-content">
          <h1 className="home-title">{'Welcome to Intelligent system'.toUpperCase()}</h1>
          <p className="home-subtitle">Authorized Personnel Only</p>
          <button className="login-btn" onClick={handleLogin}>
            LOGIN
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;