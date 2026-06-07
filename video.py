import yt_dlp
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cobalt API List
APIS = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ⚡ STEP 1: INFO FETCHING (yt-dlp use करेंगे, जो पहले चल रहा था)
@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extractor_args': {'youtube': ['player_client=android']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Unknown Title'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": f"Info failed: {str(e)}"})

# ⚡ STEP 2: DOWNLOAD (API use करेंगे, ताकि Bot Error न आए)
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
        
    return jsonify({"success": False, "error": "All download servers are currently busy."})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
