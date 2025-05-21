from flask import Flask, jsonify, request, redirect, send_file
from flask_cors import CORS
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from fpdf import FPDF
import spotipy

load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔥 THIS is the missing part:
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="https://spotifytopdf.ngrok.app",
    scope="user-library-read playlist-read-private"
)

@app.route("/")
def home():
    return "Flask is working ✅"

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/export", methods=["POST"])
def export():
    data = request.get_json()
    token = data.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    sp = spotipy.Spotify(auth=token)

    # === Load Fonts ===
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("NotoSans", "", os.path.join(font_dir, "NotoSans-Medium.ttf"), uni=True)
    pdf.add_font("NotoSans", "B", os.path.join(font_dir, "NotoSans-Bold.ttf"), uni=True)
    pdf.add_font("NotoSans", "I", os.path.join(font_dir, "NotoSans-Italic.ttf"), uni=True)

    # === Liked Songs (limit to 50) ===
    liked_tracks = []
    MAX_TRACKS = 50
    track_count = 0

    results = sp.current_user_saved_tracks(limit=50)
    while results and track_count < MAX_TRACKS:
        for item in results['items']:
            track = item['track']
            artist = track['artists'][0]['name']
            song = track['name']
            liked_tracks.append((artist, song))
            track_count += 1
            if track_count >= MAX_TRACKS:
                break
        if track_count < MAX_TRACKS and results['next']:
            results = sp.next(results)
        else:
            break

    # === Playlists (limit to first 3) ===
    playlists = sp.current_user_playlists()
    playlist_data = {}
    for playlist in playlists['items'][:3]:
        tracks = []
        tracks_data = sp.playlist_tracks(playlist['id'])
        for item in tracks_data['items']:
            track = item['track']
            if track:
                artist = track['artists'][0]['name']
                song = track['name']
                tracks.append((artist, song))
        playlist_data[playlist['name']] = tracks

    # === Liked Songs Section ===
    pdf.set_font("NotoSans", "B", 16)
    pdf.cell(0, 10, "🎵 Liked Songs", ln=True)
    pdf.ln(5)

    for i, (artist, song) in enumerate(liked_tracks):
        pdf.set_font("NotoSans", "", 12)
        pdf.multi_cell(0, 10, f"{i+1}. {artist} – {song}")
        pdf.ln(1)

    # === Playlist Sections ===
    for playlist, tracks in playlist_data.items():
        pdf.add_page()
        pdf.set_font("NotoSans", "B", 16)
        pdf.cell(0, 10, f"📂 Playlist: {playlist}", ln=True)
        pdf.ln(5)

        for i, (artist, song) in enumerate(tracks):
            pdf.set_font("NotoSans", "", 12)
            pdf.multi_cell(0, 10, f"{i+1}. {artist} – {song}")
            pdf.ln(1)

    # === Write PDF to file ===
    pdf_path = os.path.join(os.path.dirname(__file__), "spotify_export.pdf")
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

