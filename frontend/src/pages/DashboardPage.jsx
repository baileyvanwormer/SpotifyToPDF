import { useEffect, useState } from "react";
import ExportPDFButton from "../components/ExportPDFButton";
import ExportExcelButton from "../components/ExportExcelButton";

const DashboardPage = () => {
  const [likedSongs, setLikedSongs] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [includeLiked, setIncludeLiked] = useState(true);
  const [likedLimit, setLikedLimit] = useState(50);
  const [selectedPlaylists, setSelectedPlaylists] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await fetch(`https://spotifytopdf.ngrok.app/dashboard`, {
          credentials: "include", // 🔑 send secure cookie
        });

        if (res.status === 401) {
          window.location.href = "/";
          return;
        }

        const data = await res.json();
        setLikedSongs(data.liked_songs || []);
        setPlaylists(data.playlists || []);
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      }
    };

    fetchDashboardData();
  }, []);

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
        <ExportPDFButton
          includeLiked={includeLiked}
          playlistIds={selectedPlaylists}
          likedLimit={likedLimit}
        />
        <ExportExcelButton
          includeLiked={includeLiked}
          playlistIds={selectedPlaylists}
          likedLimit={likedLimit}
        />
      </div>
    </div>
  );
};

export default DashboardPage;