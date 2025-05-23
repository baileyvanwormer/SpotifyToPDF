import { useEffect, useState } from "react";
import LoginButton from "./components/LoginButton";
import ExportPDFButton from "./components/ExportPDFButton";
import ExportExcelButton from "./components/ExportExcelButton";

function App() {
  const [accessToken, setAccessToken] = useState(null);

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
          <p>You’re logged in. Click below to create your personalized export.</p>
          <div style={{ display: "flex", gap: "1rem" }}>
            <ExportPDFButton token={accessToken} includeLiked={true} playlistIds={[]} />
            <ExportExcelButton token={accessToken} includeLiked={true} playlistIds={[]} />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
