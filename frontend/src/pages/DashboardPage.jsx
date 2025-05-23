import { useEffect, useState } from "react";
import ExportPDFButton from "../components/ExportPDFButton";
import ExportExcelButton from "../components/ExportExcelButton";

const DashboardPage = () => {
  const [likedSongs, setLikedSongs] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [includeLiked, setIncludeLiked] = useState(true);
  const [selectedPlaylists, setSelectedPlaylists] = useState([]);
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/dashboard`, {
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

      <div style={{ display: "flex", gap: "1rem" }}>
        <ExportPDFButton token={token} includeLiked={includeLiked} playlistIds={selectedPlaylists} />
        <ExportExcelButton token={token} includeLiked={includeLiked} playlistIds={selectedPlaylists} />
      </div>
    </div>
  );
};

export default DashboardPage;
