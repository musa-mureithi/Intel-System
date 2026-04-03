import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

const BASE_URL = "http://127.0.0.1:8000";

const Login = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "", otp_code: "" });
  const [step, setStep] = useState("login"); 
  const [qrCode, setQrCode] = useState(null);
  const [message, setMessage] = useState("");
  const [dangerAlert, setDangerAlert] = useState(false); 
  const audioRef = useRef(null); 

  
  useEffect(() => {
    if (dangerAlert) {
      audioRef.current = new Audio("/danger_alert.mp3");
      audioRef.current.loop = true;
      audioRef.current.play();
    } else if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, [dangerAlert]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async () => {
    setMessage("");
    setDangerAlert(false);

    try {
      const res = await fetch(`${BASE_URL}/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessage(data.message || "Server error");
        if (data.danger_alert) setDangerAlert(true); 
        return;
      }

      setDangerAlert(false); 

      switch (data.status) {
        case "error":
          setMessage(data.message);
          break;

        case "require_otp":
          setStep("otp");
          setMessage(data.message);
          break;

        case "setup_2fa":
          setStep("setup");
          setQrCode(data.qr_code);
          setMessage(data.message);
          break;

        case "success":
          localStorage.setItem("access_token", data.access);
          localStorage.setItem("profile", JSON.stringify(data.profile));
          setMessage("Login successful");
          navigate("/dashboard");
          break;

        default:
          setMessage("Unexpected server response");
      }
    } catch (error) {
      console.error(error);
      setMessage("Network error");
    }
  };

  return (
    <div className={`home-container ${dangerAlert ? "shake" : ""}`}> 
      <div className="overlay">
        <div className="home-content">
          <h2 className="home-title">SECURE LOGIN</h2>
          {message && <p className={`home-subtitle ${dangerAlert ? "blink-red" : ""}`}>{message}</p>}

          {step === "login" && (
            <>
              <input type="text" name="username" placeholder="Username" onChange={handleChange} />
              <input type="password" name="password" placeholder="Password" onChange={handleChange} />
              <button onClick={handleSubmit}>AUTHENTICATE</button>
            </>
          )}

          {step === "otp" && (
            <>
              <input type="text" name="otp_code" placeholder="Enter OTP" onChange={handleChange} />
              <button onClick={handleSubmit}>VERIFY OTP</button>
            </>
          )}

          {step === "setup" && (
            <>
              {qrCode && <img src={`data:image/png;base64,${qrCode}`} alt="QR Code" />}
              <input type="text" name="otp_code" placeholder="Enter OTP" onChange={handleChange} />
              <button onClick={handleSubmit}>COMPLETE SETUP</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Login;