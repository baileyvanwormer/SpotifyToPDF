from flask import Flask, json, jsonify, request, redirect, send_file, send_from_directory, make_response
from flask_cors import CORS, cross_origin
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
from uuid import uuid4
import redis
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__, static_folder="../frontend/dist")
CORS(app, supports_credentials=True, origins=[
    "https://exportmymusic.com",
    "https://www.exportmymusic.com"
])

@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "https://www.exportmymusic.com")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

print("🚀 Flask app is running from:", __file__)

from urllib.parse import urlparse

# Parse Redis URL from environment variable
redis_url = os.getenv("REDIS_URL")
parsed_url = urlparse(redis_url)

r = redis.Redis(
    host=parsed_url.hostname,
    port=parsed_url.port,
    username=parsed_url.username,
    password=parsed_url.password,
    ssl=parsed_url.scheme == "rediss"
)

# 🔥 THIS is the missing part:
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="https://exportmymusic.com/callback",
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

    raw = r.get(f"session:{session_token}")
    token_info = json.loads(raw)

    # Refresh if token is expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        r.setex(f"session:{session_token}", 3600, json.dumps(token_info))  # update Redis

    access_token = token_info["access_token"]
    sp = spotipy.Spotify(auth=access_token)

    print(f"🧠 Redis lookup for session:{session_token} → {access_token}")

    if not access_token:
        return jsonify({"error": "Session expired or invalid"}), 403

    try:
        # ✅ Just fetch 1 liked song to get the total count
        liked_response = sp.current_user_saved_tracks(limit=1)
        liked_total = liked_response['total']

        liked_songs = [{
            "name": t['track']['name'],
            "artist": t['track']['artists'][0]['name'],
            "id": t['track']['id']
        } for t in liked_response['items']]

        # ✅ Get playlists with image URLs
        playlists = sp.current_user_playlists()
        playlist_list = [{
            "name": p['name'],
            "id": p['id'],
            "track_count": p['tracks']['total'],
            "image": p['images'][0]['url'] if p['images'] else None
        } for p in playlists['items']]

        return jsonify({
            "liked_songs": liked_songs,
            "liked_total": liked_total,
            "playlists": playlist_list
        })

    except spotipy.SpotifyException as e:
        return jsonify({"error": str(e)}), 401

# POST: send user Spotify access token to fetch Liked Songs and Playlist data from Spotify API
@app.route("/export", methods=["POST"])
def export():
    token = request.cookies.get("session_token")
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
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 401

    print("🔑 Token (partial) before generate excel call:", token[:10])
    data = request.get_json()
    include_liked = data.get("include_liked", True)
    playlist_ids = data.get("playlist_ids", [])
    liked_limit = data.get("liked_limit", 50)

    task = generate_excel.delay(token, include_liked, playlist_ids, liked_limit)
    return jsonify({"task_id": task.id, "status": "processing"}), 202

# @app.route("/callback")
# def callback():
#     resp = make_response("✅ Callback reached. Cookie should be set.")
#     sp_oauth = SpotifyOAuth(
#         client_id=os.getenv("SPOTIPY_CLIENT_ID"),
#         client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
#         redirect_uri="https://exportmymusic.com/callback",
#         scope="user-library-read playlist-read-private"
#     )

#     code = request.args.get("code")
#     if not code:
#         return "Authorization code not found", 400

#     token_info = sp_oauth.get_access_token(code)
#     access_token = token_info['access_token']

#     # ✅ Generate and store session token
#     session_token = str(uuid4())
#     r.setex(f"session:{session_token}", 3600, access_token)
#     print(f"✅ Stored session:{session_token} → {access_token}")

#     # ✅ Set session_token in cookie instead of session_token
#     resp = make_response(f"""
#     <html>
#     <body>
#         <h1>✅ Session cookie set</h1>
#         <p>session_token: {session_token}</p>
#         <p><a href="https://spotify-to-pdf.vercel.app/dash">Continue to dashboard</a></p>
#     </body>
#     </html>
#     """)
#     resp.set_cookie(
#         "session_token",
#         session_token,
#         httponly=True,
#         secure=True,
#         samesite="None",
#         max_age=3600
#     )
#     return resp

@app.route("/exchange", methods=["POST"])
@cross_origin(origins="https://exportmymusic.com", supports_credentials=True)
def exchange_code():
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "Missing code"}), 400

    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="https://exportmymusic.com/callback",
        scope="user-library-read playlist-read-private"
    )

    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    session_token = str(uuid4())
    r.setex(f"session:{session_token}", 3600, json.dumps(token_info))


    resp = jsonify({"message": "✅ Session created"})
    resp.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=True,
        samesite="None",  # Must be exactly like this, with capital "N"
        max_age=3600,
        domain=".exportmymusic.com"
    )
    print(f"✅ Setting session_token cookie: {session_token}")

    return resp

@app.route("/status/<task_id>")
def check_status(task_id):
    result = AsyncResult(task_id, app=celery_app)
    response = {"status": result.status}

    if result.ready():
        try:
            response["result"] = result.get()
        except Exception as e:
            response["status"] = "FAILURE"
            response["result"] = str(e)  # Ensure it's serializable

    else:
        response["result"] = None

    return jsonify(response)

@app.route("/download/<task_id>")
def download_file(task_id):
    result = AsyncResult(task_id, app=celery_app)

    if not result.ready():
        print("⏳ Task not ready")
        return jsonify({"status": "processing"}), 202

    file_url = result.result  # now an S3 URL
    print(f"📦 S3 file ready at: {file_url}")

    if not file_url or not file_url.startswith("https://"):
        print("❌ Invalid file URL!")
        return jsonify({"error": "Invalid file URL"}), 404

    return redirect(file_url)

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