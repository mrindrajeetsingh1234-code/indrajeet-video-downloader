import yt_dlp
import requests
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API List for Downloads
APIS = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# 🚀 404 Fix: यह आपकी वेबसाइट को रूट पर दिखाएगा
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# ⚡ STEP 1: INFO (yt-dlp use किया है ताकि Title/Thumb पक्का आए)
@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'extractor_args': {'youtube': ['player_client=android']}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'YouTube Video'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ⚡ STEP 2: DOWNLOAD (API use किया है ताकि Error न आए)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    payload = {
        "url": url,
        "videoQuality": "720" if "720" in quality else "1080",
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3"
    }

    for api in APIS:
        try:
            resp = requests.post(api, json=payload, headers=HEADERS, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                if "url" in data:
                    return jsonify({"success": True, "direct_url": data["url"]})
        except: continue
        
    return jsonify({"success": False, "error": "Traffic high, try again!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
