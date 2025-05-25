const ExportExcelButton = ({ includeLiked, playlistIds, likedLimit }) => {
  const handleExport = async () => {
    console.log("Exporting Excel:", { includeLiked, playlistIds });

    try {
      const res = await fetch(`https://spotifytopdf.ngrok.app/exportxlsx`, {
        method: "POST",
        credentials: "include", // 👈 Send the cookie!
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          include_liked: includeLiked,
          playlist_ids: playlistIds,
          liked_limit: likedLimit,
        }),
      });

      if (!res.ok) {
        throw new Error(`Export failed with status ${res.status}`);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "spotify_export.xlsx";
      a.click();
    } catch (err) {
      console.error("Excel export error:", err);
      alert("Excel export failed.");
    }
  };

  return <button onClick={handleExport}>Export Excel</button>;
};

export default ExportExcelButton;