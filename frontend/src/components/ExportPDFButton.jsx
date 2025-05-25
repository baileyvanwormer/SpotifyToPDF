const ExportPDFButton = ({ includeLiked, playlistIds, likedLimit }) => {
  const handleExport = async () => {
    console.log("Exporting PDF:", { includeLiked, playlistIds });

    try {
      const res = await fetch(`https://spotifytopdf.ngrok.app/export`, {
        method: "POST",
        credentials: "include", // 👈 this sends the HTTP-only cookie
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
      a.download = "spotify_export.pdf";
      a.click();
    } catch (err) {
      console.error("PDF export error:", err);
      alert("PDF export failed.");
    }
  };

  return <button onClick={handleExport}>Export PDF</button>;
};

export default ExportPDFButton;

  