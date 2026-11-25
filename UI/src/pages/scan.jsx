import {useEffect, useRef, useState } from "react";

const BASE_URL = "https://75lsvb8q-8000.inc1.devtunnels.ms";

function Scan() {
  const [image, setImage] = useState(null);
  const [identity, setIdentity] = useState("");
  const [dna, setDna] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (err) {
      console.error(err);
      setError("Camera access denied");
    }
  };
  const captureImage = async () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (!video || !video.videoWidth || !video.videoHeight) {
        setError("Camera not ready yet. Start the camera first.");
        return null;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    return new Promise((resolve) => {
        canvas.toBlob(
            (blob) => resolve(blob),
            "image/jpeg",
            0.9
        );
    });
};

  const handleSearch = async (useCamera = false) => {
    setError("");
    setResult(null);

    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No token found.");
      

      const formData = new FormData();

      if (useCamera) {
    const blob = await captureImage();

    if (!blob) return;

    formData.append("image_file", blob, "capture.jpg");

    } else if (image) {
      formData.append("image_file", image);
    }

      if (identity) formData.append("identity_number", identity);
      if (dna) formData.append("dna_id", dna);

      const res = await fetch(`${BASE_URL}/unified_search/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || "Search failed");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  {/*STOP'S THE CAMERA WHEN THE CAPTURE IS OVER */}
useEffect(() => {
    return () => {
        const stream = videoRef.current?.srcObject;

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    };
}, []);


  return (
    <div className="container">
      <h1 style={{ color: "white" }}> {'search'.toUpperCase()}</h1>

      <input type="file" onChange={(e) => setImage(e.target.files[0])} />
      <input
        placeholder="Identity Number"
        value={identity}
        onChange={(e) => setIdentity(e.target.value)}
      />

      <input
        placeholder="DNA ID"
        value={dna}
        onChange={(e) => setDna(e.target.value)}
      />

      <div style={{ marginTop: "15px" }}>
        <video ref={videoRef} autoPlay playsInline width="250" />
        <canvas ref={canvasRef} style={{ display: "none" }} />

        <br />

        <button onClick={startCamera}>Start Camera</button>
        <button onClick={() => handleSearch(true)}>Scan with Camera</button>
      </div>
      <button onClick={() => handleSearch(false)}>Search</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && (
        <div className="card">
          <h3>{result.full_name}</h3>
          <p>Type: {result.person_type}</p>
          <p>Blood: {result.blood_type}</p>
          <p>Status: {result.status}</p>
          <p>DNA: {result.id_dna}</p>
          <p>UNIT : {result.unit_type}</p>
          <p>OPs: {result.OperationAssignment.join(", ")}</p>
          

          {result.match_confidence && <p>Confidence: {result.match_confidence}</p>}

          {result.image && <img src={result.image} alt="" width="150" />}
        </div>
      )}
    </div>
  );
}

export default Scan;