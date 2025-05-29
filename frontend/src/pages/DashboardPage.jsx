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
        setLikedSongs(data.liked_songs || []);
        setLikedTotal(data.liked_total || 0);
        setPlaylists(data.playlists || []);

        // Default likedLimit to the smaller of 50 or actual liked songs
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
  
      // Automatically update the "Select All" checkbox state
      setSelectAll(newSelection.length === playlists.length);
  
      return newSelection;
    });
  };  

  const handleSelectAll = (checked) => {
    setSelectAll(checked);
    setSelectedPlaylists(checked ? playlists.map(p => p.id) : []);
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
      <h3>Select Playlists</h3>
      <label style={{ display: "block", marginBottom: "0.5rem" }}>
        <input
          type="checkbox"
          checked={selectAll}
          onChange={(e) => handleSelectAll(e.target.checked)}
        />
        Select All Playlists
      </label>

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