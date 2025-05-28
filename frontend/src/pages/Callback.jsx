import { useEffect } from "react";

const Callback = () => {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");

    if (!code) {
      console.error("Missing code from Spotify");
      return;
    }

    fetch("https://backend-production-4f70.up.railway.app/exchange", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // IMPORTANT to accept the session_token cookie
      body: JSON.stringify({ code }),
    })
      .then((res) => res.json())
      .then(() => {
        window.location.href = "https://spotify-to-pdf.vercel.app/dash";
      })
      .catch((err) => {
        console.error("Token exchange failed", err);
        alert("Authentication failed. Please try logging in again.");
      });
  }, []);

  return <h2>Connecting to Spotify…</h2>;
};

export default Callback;
