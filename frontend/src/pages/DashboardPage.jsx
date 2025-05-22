import { useEffect, useState } from "react";

const DashboardPage = () => {
  const [likedSongs, setLikedSongs] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [includeLiked, setIncludeLiked] = useState(true);
  const [selectedPlaylists, setSelectedPlaylists] = useState([]);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await fetch("https://spotifytopdf.ngrok.app/dashboard", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const data = await res.json();
        setLikedSongs(data.liked_songs || []);
        setPlaylists(data.playlists || []);
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      }
    };

    if (token) fetchDashboardData();
  }, [token]);

  const togglePlaylist = (playlistId) => {
    setSelectedPlaylists((prev) =>
      prev.includes(playlistId)
        ? prev.filter((id) => id !== playlistId)
        : [...prev, playlistId]
    );
  };

  const handleExport = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/export`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          include_liked: includeLiked,
          playlist_ids: selectedPlaylists,
        }),
      });

      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "spotify_export.pdf";
      a.click();
    } catch (err) {
      console.error("Export failed:", err);
      alert("Export failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h2>🎧 Customize Your Export</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            type="checkbox"
            checked={includeLiked}
            onChange={(e) => setIncludeLiked(e.target.checked)}
          />
          Include Liked Songs ({likedSongs.length})
        </label>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <h3>Select Playlists</h3>
        {playlists.map((playlist) => (
          <label key={playlist.id} style={{ display: "block", marginBottom: "0.5rem" }}>
            <input
              type="checkbox"
              checked={selectedPlaylists.includes(playlist.id)}
              onChange={() => togglePlaylist(playlist.id)}
            />
            {playlist.name} ({playlist.track_count})
          </label>
        ))}
      </div>

      <button onClick={handleExport} disabled={loading}>
        {loading ? "Generating PDF..." : "Export My Spotify Data"}
      </button>
    </div>
  );
};

export default DashboardPage;
