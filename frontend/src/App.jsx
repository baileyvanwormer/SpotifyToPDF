import { useEffect, useState } from "react";
import LoginButton from "./components/LoginButton";
import ExportButton from "./components/ExportButton";

function App() {
  const [accessToken, setAccessToken] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | exporting | done | error

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tokenFromURL = params.get("access_token");
    const tokenFromStorage = localStorage.getItem("access_token");

    if (tokenFromURL) {
      localStorage.setItem("access_token", tokenFromURL);
      setAccessToken(tokenFromURL);
      window.history.replaceState({}, document.title, "/"); // Clean URL
    } else if (tokenFromStorage) {
      setAccessToken(tokenFromStorage);
    }
  }, []);

  const handleExport = async () => {
    setStatus("exporting");
    try {
      const res = await fetch("https://spotifytopdf.ngrok.app/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          include_liked: true,
          playlist_ids: [], // optionally update this later
        }),
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
