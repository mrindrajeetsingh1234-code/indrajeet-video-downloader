import os
import urllib.request
import json
import re
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "🚀 Indrajeet Ultra-Fast Backend Running!"})

# ⚡ STEP 1: VIDEO INFO
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True, 'no_warnings': True, 'noplaylist': True,
            'extract_flat': 'in_playlist',
            'extractor_args': {'youtube': ['player_client=ios,android,tv,web']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            thumb = info.get('thumbnail', '')
            formats = info.get('formats', [])
            live_res = {f.get('height') for f in formats if f.get('vcodec') != 'none' and f.get('height')}
            final_qualities = [f"{res}p" for res in sorted(list(live_res), reverse=True)[:4]]
            if not final_qualities: final_qualities = ["1080p", "720p", "480p"]
            final_qualities.append("Audio (MP3)")

            return jsonify({"success": True, "title": title, "thumb": thumb, "metadata": f"Title: {title}\nLink: {url}", "qualities": final_qualities})
    except:
        return jsonify({"success": True, "title": "YouTube Video", "thumb": "", "metadata": f"Link: {url}", "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]})

# ⚡ STEP 2: DIRECT FAST DOWNLOAD (V7 API COMPATIBLE)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    v_quality = "1080"
    if "720" in quality: v_quality = "720"
    elif "480" in quality: v_quality = "480"

    # Cobalt v7 API Payload
    payload = json.dumps({
        "url": url,
        "videoQuality": v_quality,
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3",
        "filenamePattern": "classic"
    }).encode('utf-8')
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    # API List (Main + Backups)
    apis = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]
    
    for api in apis:
        try:
            req = urllib.request.Request(api, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode())
                if "url" in res:
                    return jsonify({"success": True, "direct_url": res["url"]})
        except:
            continue

    return jsonify({"success": False, "error": "Servers are busy. Try again!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=False)
