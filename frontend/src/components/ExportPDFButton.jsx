import React from "react";

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

          console.log("status:", status);
          console.log("result:", result);

          if (status === "SUCCESS" && result) {
            console.log("✅ PDF file ready at:", result);

            const link = document.createElement("a");
            link.href = result;
            link.download = "spotify_export.pdf";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
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