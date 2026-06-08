import yt_dlp
import os
import threading
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🚀 Server Sleep se bachne ke liye Auto-Ping logic
def keep_alive():
    while True:
        try:
            # Apne Render URL ko yahan update karein
            requests.get("https://indrajeet-video-downloader.onrender.com")
        except: pass
        time.sleep(300) # Har 5 minute mein khud ko ping karega

threading.Thread(target=keep_alive, daemon=True).start()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    try:
        ydl_opts = {'quiet': True, 'extractor_args': {'youtube': ['player_client=android']}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True, 
                "title": info.get('title'), 
                "thumb": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Platform Error"})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'extractor_args': {'youtube': ['player_client=android']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            link = info.get('url') or info.get('formats')[-1]['url']
            return jsonify({"success": True, "direct_url": link})
    except Exception as e:
        return jsonify({"success": False, "error": "Try again, link protected."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
