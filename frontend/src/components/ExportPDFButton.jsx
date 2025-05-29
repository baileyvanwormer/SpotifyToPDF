const ExportPDFButton = ({ includeLiked, playlistIds, likedLimit }) => {
  const handleExport = async () => {
    try {
      const res = await fetch("https://api.exportmymusic.com/export", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          include_liked: includeLiked,
          playlist_ids: playlistIds,
          liked_limit: likedLimit,
        }),
      });

      if (!res.ok) throw new Error("Failed to start export");

      const { task_id } = await res.json();
      console.log("📄 PDF task started:", task_id);

      const pollStatus = async () => {
        try {
          const statusRes = await fetch(`https://api.exportmymusic.com/status/${task_id}`);
          const { status, result } = await statusRes.json();

          if (status === "SUCCESS" && result) {
            const downloadRes = await fetch(`https://api.exportmymusic.com/download/${task_id}`, {
              method: "GET",
              credentials: "include",
            });

            if (downloadRes.status === 200) {
              console.log("✅ PDF ready, downloading...");

              const blob = await downloadRes.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "spotify_export.pdf";
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            } else if (downloadRes.status === 202) {
              console.log("⏳ PDF file not ready yet, retrying...");
              setTimeout(pollStatus, 1000);
            } else {
              throw new Error("Unexpected download status");
            }
          } else if (status === "FAILURE") {
            alert("PDF export failed.");
          } else {
            setTimeout(pollStatus, 1000);
          }
        } catch (err) {
          console.error("Polling error:", err);
          setTimeout(pollStatus, 1500);
        }
      };

      pollStatus();
    } catch (err) {
      console.error("PDF export error:", err);
      alert("PDF export failed.");
    }
  };

  return <button onClick={handleExport}>Export PDF</button>;
};

export default ExportPDFButton;