from flask import Flask, jsonify, request, redirect, send_file
from flask_cors import CORS
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from fpdf import FPDF
import spotipy
from datetime import datetime
from urllib.parse import urlencode
import pandas as pd
import openpyxl

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

# initial home page
@app.route("/")
def home():
    code = request.args.get("code")
    if code:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info["access_token"]
        print(access_token)
        # return access_token # comment out and uncomment below code when using with frontend, this is for backend testing only

        # Redirect to frontend with token in query string
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/dashboard?" + urlencode({"access_token": access_token})
        return redirect(redirect_url)

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# GET: authenticate Spotify user using Spotify API
@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# GET: fetch Liked songs and Playlists for a user using Spotify API
@app.route("/dashboard", methods=["GET"])
def dashboard():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.replace("Bearer ", "")


    if not token:
        return jsonify({"error": "Missing token"}), 400

    sp = spotipy.Spotify(auth=token)

    try:
        # Get liked songs
        liked = sp.current_user_saved_tracks(limit=50)
        liked_songs = [{
            "name": t['track']['name'],
            "artist": t['track']['artists'][0]['name'],
            "id": t['track']['id']
        } for t in liked['items']]

        # Get playlists
        playlists = sp.current_user_playlists()
        playlist_list = [{
            "name": p['name'],
            "id": p['id'],
            "track_count": p['tracks']['total']
        } for p in playlists['items']]

        return jsonify({
            "liked_songs": liked_songs,
            "playlists": playlist_list
        })

    except spotipy.SpotifyException as e:
        return jsonify({"error": str(e)}), 401

# POST: send user Spotify access token to fetch Liked Songs and Playlist data from Spotify API
@app.route("/export", methods=["POST"])
def export():
    print("🟢 /export called")
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.replace("Bearer ", "")
    sp = spotipy.Spotify(auth=token)

    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])

    print("INCLUDE LIKED:", include_liked)
    print("PLAYLIST IDS:", playlist_ids)    

    # === Set up PDF ===
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("NotoSans", "", os.path.join(font_dir, "NotoSans-Medium.ttf"), uni=True)
    pdf.add_font("NotoSans", "B", os.path.join(font_dir, "NotoSans-Bold.ttf"), uni=True)
    pdf.add_font("NotoSans", "I", os.path.join(font_dir, "NotoSans-Italic.ttf"), uni=True)

    # === Liked Songs Section ===
    if include_liked:
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

        now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        pdf.set_font("NotoSans", "I", 10)
        pdf.cell(0, 10, f"Exported on {now}", ln=True)
        pdf.ln(5)

        pdf.set_font("NotoSans", "B", 16)
        pdf.cell(0, 10, "🎵 Liked Songs", ln=True)
        pdf.ln(5)

        for i, (artist, song) in enumerate(liked_tracks):
            pdf.set_font("NotoSans", "", 12)
            pdf.multi_cell(0, 10, f"{i+1}. {artist} – {song}")
            pdf.ln(1)

    # === Selected Playlists ===
    for pid in playlist_ids:
        playlist = sp.playlist(pid)
        tracks_data = sp.playlist_tracks(pid)
        tracks = []

        for item in tracks_data['items']:
            track = item['track']
            if track:
                artist = track['artists'][0]['name']
                song = track['name']
                tracks.append((artist, song))

        pdf.add_page()
        pdf.set_font("NotoSans", "B", 16)
        pdf.cell(0, 10, f"📂 Playlist: {playlist['name']}", ln=True)
        pdf.ln(5)

        for i, (artist, song) in enumerate(tracks):
            pdf.set_font("NotoSans", "", 12)
            pdf.multi_cell(0, 10, f"{i+1}. {artist} – {song}")
            pdf.ln(1)

    # === Write and Return PDF ===
    pdf_path = os.path.join(os.path.dirname(__file__), "spotify_export.pdf")
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

@app.route("/exportxlsx", methods=["POST"])
def export_xlsx():
    print("🟢 /exportxlsx called")
    # Get access token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.replace("Bearer ", "")
    sp = spotipy.Spotify(auth=token)

    # Parse request JSON
    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])

    rows = []

    try:
        # Liked Songs
        if include_liked:
            liked_tracks = sp.current_user_saved_tracks(limit=50)
            for item in liked_tracks['items']:
                track = item['track']
                rows.append({
                    "Source": "Liked Songs",
                    "Track": track['name'],
                    "Artist": track['artists'][0]['name'],
                    "Album": track['album']['name'],
                    "Duration (min)": round(track['duration_ms'] / 60000, 2)
                })

        # Selected Playlists
        for pid in playlist_ids:
            playlist = sp.playlist(pid)
            playlist_name = playlist['name']
            tracks_data = sp.playlist_tracks(pid)

            for item in tracks_data['items']:
                track = item['track']
                if track:
                    rows.append({
                        "Source": playlist_name,
                        "Track": track['name'],
                        "Artist": track['artists'][0]['name'],
                        "Album": track['album']['name'],
                        "Duration (min)": round(track['duration_ms'] / 60000, 2)
                    })

        # Convert to DataFrame and save as Excel
        df = pd.DataFrame(rows)[["Source", "Artist", "Track", "Album", "Duration (min)"]]
        xlsx_path = os.path.join(os.path.dirname(__file__), "spotify_export.xlsx")
        df.to_excel(xlsx_path, index=False)

        # Open the Excel file for editing
        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb.active

        # Set custom column widths (A = Source, B = Artist, etc.)
        column_widths = {
            "A": 20,
            "B": 25,
            "C": 35,
            "D": 30,
            "E": 15,
        }

        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

        # Save changes
        wb.save(xlsx_path)

        return send_file(xlsx_path, as_attachment=True)

    except Exception as e:
        print("Export error:", e)
        return jsonify({"error": "Export to Excel failed"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

