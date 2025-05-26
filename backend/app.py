from flask import Flask, jsonify, request, redirect, send_file, send_from_directory, make_response
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
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

app = Flask(__name__, static_folder="../frontend/dist")
CORS(app)

print("🚀 Flask app is running from:", __file__)


# 🔥 THIS is the missing part:
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="https://spotifytopdf.ngrok.app/callback",
    scope="user-library-read playlist-read-private"
)

# GET: authenticate Spotify user using Spotify API
@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    print(f"Redirecting to: {auth_url}")
    return redirect(auth_url)

# GET: fetch Liked songs and Playlists for a user using Spotify API
@app.route("/dashboard", methods=["GET"])
def dashboard():
    token = request.cookies.get("spotify_token")
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 401

    sp = spotipy.Spotify(auth=token)

    try:
        # ✅ Just fetch 1 liked song to get the total count
        liked_response = sp.current_user_saved_tracks(limit=1)
        liked_total = liked_response['total']

        # ✅ You can skip collecting songs here if you’re only showing total
        # or leave this empty or limited to 1
        liked_songs = [{
            "name": t['track']['name'],
            "artist": t['track']['artists'][0]['name'],
            "id": t['track']['id']
        } for t in liked_response['items']]

        # ✅ Get playlists as usual
        playlists = sp.current_user_playlists()
        playlist_list = [{
            "name": p['name'],
            "id": p['id'],
            "track_count": p['tracks']['total']
        } for p in playlists['items']]

        return jsonify({
            "liked_songs": liked_songs,  # can be empty or preview only
            "liked_total": liked_total,  # ✅ new!
            "playlists": playlist_list
        })

    except spotipy.SpotifyException as e:
        return jsonify({"error": str(e)}), 401


# POST: send user Spotify access token to fetch Liked Songs and Playlist data from Spotify API
@app.route("/export", methods=["POST"])
def export():
    print("🟢 /export called")

    token = request.cookies.get("spotify_token")
    if not token:
        print("❌ Missing token in cookies for /export")
        return jsonify({"error": "Missing or invalid token"}), 401

    sp = spotipy.Spotify(auth=token)

    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])
    liked_limit = data.get("liked_limit", 50)

    print("INCLUDE LIKED:", include_liked)
    print("PLAYLIST IDS:", playlist_ids)
    print("LIKED LIMIT:", liked_limit)

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
        MAX_SPOTIFY_LIMIT = 50
        fetched = 0

        while fetched < liked_limit:
            to_fetch = min(MAX_SPOTIFY_LIMIT, liked_limit - fetched)
            print(f"Fetching liked songs: offset={fetched}, limit={to_fetch}")
            results = sp.current_user_saved_tracks(limit=to_fetch, offset=fetched)

            for item in results['items']:
                track = item['track']
                artist = track['artists'][0]['name']
                song = track['name']
                liked_tracks.append((artist, song))

            fetched += to_fetch

            if not results.get('next'):
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

    # ✅ Get token from cookie
    token = request.cookies.get("spotify_token")
    if not token:
        print("❌ Missing token in cookies for /exportxlsx")
        return jsonify({"error": "Missing or invalid token"}), 401

    sp = spotipy.Spotify(auth=token)

    # Parse request JSON
    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])
    liked_limit = data.get("liked_limit", 50)

    rows = []

    try:
        # === Liked Songs Section (batched) ===
        if include_liked:
            MAX_SPOTIFY_LIMIT = 50
            fetched = 0

            while fetched < liked_limit:
                to_fetch = min(MAX_SPOTIFY_LIMIT, liked_limit - fetched)
                print(f"Fetching liked songs: offset={fetched}, limit={to_fetch}")
                results = sp.current_user_saved_tracks(limit=to_fetch, offset=fetched)

                for item in results['items']:
                    track = item['track']
                    rows.append({
                        "Source": "Liked Songs",
                        "Track": track['name'],
                        "Artist": track['artists'][0]['name'],
                        "Album": track['album']['name'],
                        "Duration (min)": round(track['duration_ms'] / 60000, 2)
                    })

                fetched += to_fetch

                if not results.get("next"):
                    break

        # === Selected Playlists Section ===
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

        # === Write to Excel ===
        df = pd.DataFrame(rows)[["Source", "Artist", "Track", "Album", "Duration (min)"]]
        xlsx_path = os.path.join(os.path.dirname(__file__), "spotify_export.xlsx")
        df.to_excel(xlsx_path, index=False)

        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb.active

        column_widths = {
            "A": 20,
            "B": 25,
            "C": 35,
            "D": 30,
            "E": 15,
        }

        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

        wb.save(xlsx_path)

        return send_file(xlsx_path, as_attachment=True)

    except Exception as e:
        print("Export error:", e)
        return jsonify({"error": "Export to Excel failed"}), 500

@app.route("/callback")
def callback():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="https://spotifytopdf.ngrok.app/callback",
        scope="user-library-read playlist-read-private"
    )

    code = request.args.get("code")
    if not code:
        return "Authorization code not found", 400

    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # Set a secure, HTTP-only cookie
    print("✅ Access token set. Redirecting to /dash")
    resp = make_response(redirect("/dash"))
    resp.set_cookie(
        "spotify_token",
        access_token,
        httponly=True,
        secure=True,  # ensure HTTPS only
        samesite="Lax",  # prevents CSRF in most cases
        max_age=3600     # 1 hour token lifespan
    )
    return resp

# React routes – catch-all
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    print("Requested path:", path)
    full_path = os.path.join(app.static_folder, path)
    print("Full path:", full_path)

    if path != "" and os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

