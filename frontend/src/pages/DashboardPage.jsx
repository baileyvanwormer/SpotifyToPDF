import { useEffect, useState } from "react";
import ExportPDFButton from "../components/ExportPDFButton";
import ExportExcelButton from "../components/ExportExcelButton";

const DashboardPage = () => {
  const [likedSongs, setLikedSongs] = useState([]);
  const [likedTotal, setLikedTotal] = useState(0);
  const [selectAll, setSelectAll] = useState(false);
  const [playlists, setPlaylists] = useState([]);
  const [includeLiked, setIncludeLiked] = useState(true);
  const [likedLimit, setLikedLimit] = useState(50);
  const [selectedPlaylists, setSelectedPlaylists] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await fetch(`https://api.exportmymusic.com/dashboard`, {
          credentials: "include",
        });

        if (res.status === 401) {
          window.location.href = "/";
          return;
        }

        const data = await res.json();
        console.log("🎧 Playlists:", data.playlists);
        setLikedSongs(data.liked_songs || []);
        setLikedTotal(data.liked_total || 0);
        setPlaylists(data.playlists || []);

        const defaultLimit = Math.min(50, (data.liked_songs || []).length);
        setLikedLimit(defaultLimit);
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      }
    };

    fetchDashboardData();
  }, []);

  const togglePlaylist = (playlistId) => {
    setSelectedPlaylists((prev) => {
      const newSelection = prev.includes(playlistId)
        ? prev.filter((id) => id !== playlistId)
        : [...prev, playlistId];
      setSelectAll(newSelection.length === playlists.length);
      return newSelection;
    });
  };

  const handleSelectAll = (checked) => {
    setSelectAll(checked);
    setSelectedPlaylists(checked ? playlists.map(p => p.id) : []);
  };

  return (
    <div className="dash-header" style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Select Playlists and Preferences</h1>
      <p>Choose the playlists you want to export and whether to include Liked Songs.</p>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            type="checkbox"
            checked={includeLiked}
            onChange={(e) => setIncludeLiked(e.target.checked)}
          />
          Include Liked Songs
        </label>
      </div>

      {includeLiked && likedTotal > 0 && (
        <div style={{ marginBottom: "1rem" }}>
          <label>
            How many liked songs to include:&nbsp;
            <select
              value={likedLimit}
              onChange={(e) => setLikedLimit(parseInt(e.target.value))}
            >
              <option value={1}>1</option>
              {Array.from({ length: Math.floor(likedTotal / 50) }, (_, i) => (i + 1) * 50).map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
        </div>
      )}

      <div style={{ marginBottom: "1rem" }}>
        <h3>My Playlists</h3>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          <input
            type="checkbox"
            checked={selectAll}
            onChange={(e) => handleSelectAll(e.target.checked)}
          />
          Select All Playlists
        </label>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
          {playlists.map((playlist) => (
            <div
              key={playlist.id}
              style={{
                display: "flex",
                alignItems: "center",
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "0.5rem",
                width: "300px",
              }}
            >
              <input
                type="checkbox"
                checked={selectedPlaylists.includes(playlist.id)}
                onChange={() => togglePlaylist(playlist.id)}
                style={{ marginRight: "0.75rem" }}
              />
              <img
                src={playlist.image || "/default-cover.png"}
                alt={playlist.name}
                style={{ width: "64px", height: "64px", objectFit: "cover", borderRadius: "8px", marginRight: "0.75rem" }}
              />
              <div>
                <strong>{playlist.name}</strong>
                <div style={{ fontSize: "0.85rem", color: "#666" }}>
                  {playlist.track_count} tracks
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="export-buttons">
        <ExportExcelButton
          includeLiked={includeLiked}
          playlistIds={selectedPlaylists}
          likedLimit={likedLimit}
        />
        <ExportPDFButton
          includeLiked={includeLiked}
          playlistIds={selectedPlaylists}
          likedLimit={likedLimit}
        />
      </div>
    </div>
  );
};

export default DashboardPage;