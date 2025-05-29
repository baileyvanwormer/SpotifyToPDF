# backend/tasks.py

from celery_worker import celery_app
import os
from fpdf import FPDF
import spotipy
from datetime import datetime
import pandas as pd
import openpyxl
from utils import upload_to_s3

@celery_app.task(name="tasks.generate_pdf")
def generate_pdf(token, include_liked, playlist_ids, liked_limit):
    sp = spotipy.Spotify(auth=token)

    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("NotoSans", "", os.path.join(font_dir, "NotoSans-Medium.ttf"), uni=True)
    pdf.add_font("NotoSans", "B", os.path.join(font_dir, "NotoSans-Bold.ttf"), uni=True)
    pdf.add_font("NotoSans", "I", os.path.join(font_dir, "NotoSans-Italic.ttf"), uni=True)

    if include_liked:
        liked_tracks = []
        MAX_SPOTIFY_LIMIT = 50
        fetched = 0

        while fetched < liked_limit:
            to_fetch = min(MAX_SPOTIFY_LIMIT, liked_limit - fetched)
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

    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "spotify_export.pdf"))
    with open(pdf_path, "wb") as f:
        pdf.output(f)
    return upload_to_s3(pdf_path)

@celery_app.task(name="tasks.generate_excel")
def generate_excel(token, include_liked, playlist_ids, liked_limit):
    print("🔧 Starting Excel task...")
    print("🔑 Token (partial):", token[:10])

    try:
        sp = spotipy.Spotify(auth=token)
        rows = []
        MAX_SPOTIFY_LIMIT = 50
        fetched = 0

        if include_liked:
            print("🎶 Fetching liked songs...")
            while fetched < liked_limit:
                to_fetch = min(MAX_SPOTIFY_LIMIT, liked_limit - fetched)
                results = sp.current_user_saved_tracks(limit=to_fetch, offset=fetched)
                print(f"📦 Fetched {len(results['items'])} tracks at offset {fetched}")
                for item in results['items']:
                    track = item['track']
                    rows.append({
                        "Source": "Liked Songs",
                        "Artist": track['artists'][0]['name'],  # moved up
                        "Track": track['name'],
                        "Album": track['album']['name'],
                        "Duration (min)": "{:d}:{:02d}".format(
                            (track['duration_ms'] // 60000),
                            (track['duration_ms'] // 1000) % 60
                        )
                    })
                fetched += to_fetch
                if not results.get('next'):
                    break

        for pid in playlist_ids:
            print(f"📁 Fetching playlist: {pid}")
            playlist = sp.playlist(pid)
            playlist_name = playlist['name']
            tracks_data = sp.playlist_tracks(pid)
            for item in tracks_data['items']:
                track = item['track']
                if track:
                    rows.append({
                        "Source": playlist_name,
                        "Artist": track['artists'][0]['name'],  # moved up
                        "Track": track['name'],
                        "Album": track['album']['name'],
                        "Duration (min)": "{:d}:{:02d}".format(
                            (track['duration_ms'] // 60000),
                            (track['duration_ms'] // 1000) % 60
                        )
                    })

        if not rows:
            print("⚠️ No rows collected — skipping Excel export.")
            return None

        import uuid
        filename = f"spotify_export_{uuid.uuid4().hex}.xlsx"
        xlsx_path = os.path.join(os.path.dirname(__file__), filename)
        print(f"💾 Writing Excel to: {xlsx_path}")

        df = pd.DataFrame(rows, columns=["Source", "Artist", "Track", "Album", "Duration (min)"])  # explicit order
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb.active
        column_widths = {"A": 20, "B": 25, "C": 35, "D": 30, "E": 15}
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width
        wb.save(xlsx_path)
        wb.close()

        print(f"✅ Excel complete: {xlsx_path} ({os.path.getsize(xlsx_path)} bytes)")
        return upload_to_s3(xlsx_path)  # or pdf_path

    except Exception as e:
        print("❌ Excel generation failed:", e)
        return None
