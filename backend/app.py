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
from tasks import generate_pdf, generate_excel
from celery.result import AsyncResult
from celery_worker import celery_app

load_dotenv()

app = Flask(__name__, static_folder="../frontend/dist")
CORS(app, supports_credentials=True, origins=["https://spotify-to-pdf.vercel.app"])

print("🚀 Flask app is running from:", __file__)


# 🔥 THIS is the missing part:
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="https://backend-production-4f70.up.railway.app/callback",
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
    session_token = request.cookies.get("session_token")
    print(f"🔍 Received session_token cookie: {session_token}")

    if not session_token:
        return jsonify({"error": "Missing session token"}), 401

    access_token = r.get(f"session:{session_token}")
    print(f"🧠 Redis lookup for session:{session_token} → {access_token}")

    if not access_token:
        return jsonify({"error": "Session expired or invalid"}), 403

    sp = spotipy.Spotify(auth=access_token)

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
    token = request.cookies.get("spotify_token")
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 401

    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])
    liked_limit = data.get("liked_limit", 50)

    task = generate_pdf.delay(token, include_liked, playlist_ids, liked_limit)
    return jsonify({"task_id": task.id, "status": "processing"}), 202

@app.route("/exportxlsx", methods=["POST"])
def export_xlsx():
    token = request.cookies.get("spotify_token")
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 401

    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])
    liked_limit = data.get("liked_limit", 50)

    task = generate_excel.delay(token, include_liked, playlist_ids, liked_limit)
    return jsonify({"task_id": task.id, "status": "processing"}), 202

from uuid import uuid4

@app.route("/callback")
def callback():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="https://backend-production-4f70.up.railway.app/callback",
        scope="user-library-read playlist-read-private"
    )

    code = request.args.get("code")
    if not code:
        return "Authorization code not found", 400

    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # ✅ Generate and store session token
    session_token = str(uuid4())
    r.setex(f"session:{session_token}", 3600, access_token)
    print(f"✅ Stored session:{session_token} → {access_token}")

    # ✅ Set session_token in cookie instead of spotify_token
    resp = make_response(redirect("https://spotify-to-pdf.vercel.app/dash"))
    resp.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600
    )

    # 🧹 (Optional) Clear old spotify_token if it ever existed
    resp.set_cookie("spotify_token", "", expires=0)

    return resp

@app.route("/status/<task_id>")
def check_status(task_id):
    result = AsyncResult(task_id, app=celery_app)
    return jsonify({
        "status": result.status,
        "result": result.result if result.ready() else None
    })

@app.route("/download/<task_id>")
def download_file(task_id):
    result = AsyncResult(task_id, app=celery_app)

    if not result.ready():
        print("⏳ Task not ready")
        return jsonify({"status": "processing"}), 202

    file_path = result.result
    print(f"📥 Attempting to send: {file_path}")

    if not file_path or not os.path.isfile(file_path):
        print("❌ File not found!")
        return jsonify({"error": "File not found"}), 404

    print(f"📦 Found file. Size: {os.path.getsize(file_path)} bytes")

    if file_path.endswith(".xlsx"):
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_path.endswith(".pdf"):
        mimetype = "application/pdf"
    else:
        mimetype = "application/octet-stream"

    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path),
        mimetype=mimetype
    )



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
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )