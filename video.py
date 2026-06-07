import yt_dlp
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# API List (Backup के लिए)
APIS = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]

def get_info_from_api(url):
    """अगर yt-dlp फेल हो जाए, तो API से जानकारी निकालें"""
    for api in APIS:
        try:
            resp = requests.post(api, json={"url": url}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "title": data.get("filename") or "YouTube Video",
                    "thumb": data.get("thumbnail") or "",
                    "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
                }
        except: continue
    return {"success": False, "error": "All info sources down"}

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        # कोशिश करें yt-dlp से
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': ['player_client=android']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Unknown'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
    except:
        # अगर yt-dlp फेल हुआ, तो API का उपयोग करें
        return jsonify(get_info_from_api(url))

@app.route('/download', methods=['POST'])
def download_video():
    # Download के लिए API ही सबसे बेस्ट है क्योंकि yt-dlp डाउनलोड में अक्सर फेल होता है
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    payload = {
        "url": url,
        "videoQuality": "720" if "720" in quality else "1080",
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality
    }
    
    for api in APIS:
        try:
            resp = requests.post(api, json=payload, timeout=10)
            if resp.status_code == 200:
                res = resp.json()
                if "url" in res:
                    return jsonify({"success": True, "direct_url": res["url"]})
        except: continue
    return jsonify({"success": False, "error": "Download server busy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
