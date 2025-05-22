import { useEffect, useState } from "react";
import LoginButton from "./components/LoginButton";
import ExportButton from "./components/ExportButton";

function App() {
  const [accessToken, setAccessToken] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | exporting | done | error

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");

    if (token) {
      setAccessToken(token);
      window.history.replaceState({}, document.title, "/"); // Clean URL
    }
  }, []);

  const handleExport = async () => {
    setStatus("exporting");
    try {
      const res = await fetch("http://localhost:5000/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: accessToken }),
      });

      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "spotify_export.pdf";
      a.click();

      setStatus("done");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Spotify to PDF Exporter</h1>

      {!accessToken ? (
        <>
          <p>Log in with your Spotify account to generate a PDF of your liked songs and playlists.</p>
          <LoginButton />
        </>
      ) : (
        <>
          <p>You’re logged in. Click below to create your personalized PDF export.</p>
          <ExportButton onExport={handleExport} />
          {status === "exporting" && <p>Generating PDF...</p>}
          {status === "done" && <p>✅ PDF downloaded!</p>}
          {status === "error" && <p>❌ Something went wrong. Try again.</p>}
        </>
      )}
    </div>
  );
}

export default App;
