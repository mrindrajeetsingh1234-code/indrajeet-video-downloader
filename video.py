import yt_dlp
import requests
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. API List
APIS = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]

# 2. Global YDL Options (इसमें आपके नए कमांड्स जोड़ दिए हैं)
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'format': 'best',
    'nocheckcertificate': True,
    'geo-bypass': True,
    'extractor_args': {'youtube': ['player_client=android']},
    'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36'
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    # Download के लिए API का इस्तेमाल करेंगे क्योंकि yt-dlp डाउनलोड में अक्सर ब्लॉक हो जाता है
    payload = {
        "url": url,
        "videoQuality": "720" if "720" in quality else "1080",
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3"
    }
    
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    
    for api in APIS:
        try:
            resp = requests.post(api, json=payload, headers=headers, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                if "url" in data:
                    return jsonify({"success": True, "direct_url": data["url"]})
        except: continue
        
    return jsonify({"success": False, "error": "Server busy, try again!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
