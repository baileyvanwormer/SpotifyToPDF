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
    redirect_uri="https://061c-195-202-50-83.ngrok-free.app",
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

    # Fetch liked songs
    liked_tracks = []
    results = sp.current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            liked_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
        results = sp.next(results) if results['next'] else None

    # Fetch playlists
    playlists = sp.current_user_playlists()
    playlist_data = {}
    for playlist in playlists['items']:
        tracks = []
        tracks_data = sp.playlist_tracks(playlist['id'])
        for item in tracks_data['items']:
            track = item['track']
            if track:
                tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
        playlist_data[playlist['name']] = tracks

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Liked Songs", ln=True)
    for song in liked_tracks:
        pdf.cell(200, 10, txt=song, ln=True)

    for playlist, tracks in playlist_data.items():
        pdf.add_page()
        pdf.cell(200, 10, txt=f"Playlist: {playlist}", ln=True)
        for track in tracks:
            pdf.cell(200, 10, txt=track, ln=True)

    pdf_path = "spotify_export.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
