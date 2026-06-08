import os
import yt_dlp
import threading
import time
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "temp_downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 🚀 Server Sleep se bachne ke liye Auto-Ping logic
def keep_alive():
    while True:
        try:
            # Apne Render URL ko yahan update karein (https://indrajeet-video-downloader.onrender.com)
            requests.get("https://indrajeet-video-downloader.onrender.com")
        except: pass
        time.sleep(200) # Har 3-4 minute mein ping karega

threading.Thread(target=keep_alive, daemon=True).start()

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    try:
        # Instagram/YouTube ke liye best settings
        ydl_opts = {
            'quiet': True, 
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True, 
                "title": info.get('title'), 
                "thumb": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid Link or Platform Block"})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        ydl_opts = {
            'quiet': True, 
            'format': 'best', 
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return jsonify({"success": True, "filename": os.path.basename(filename)})
    except Exception as e:
        return jsonify({"success": False, "error": "Download Error"})

@app.route('/get_file/<filename>')
def get_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
