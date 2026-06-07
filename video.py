import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚡ INFO FETCHER
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    # Requests लाइब्रेरी का इस्तेमाल (ये urllib से 100 गुना ज्यादा स्टेबल है)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    apis = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]
    
    for api in apis:
        try:
            response = requests.post(api, json={"url": url}, headers=headers, timeout=10)
            if response.status_code == 200:
                res = response.json()
                return jsonify({
                    "success": True,
                    "title": res.get("filename", "Video"),
                    "thumb": res.get("thumbnail", ""),
                    "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
                })
        except: continue
    return jsonify({"success": False, "error": "Servers busy"})

# ⚡ DOWNLOADER (The Final Fix)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "url": url,
        "videoQuality": "1080" if "720" not in quality else "720",
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3",
        "filenamePattern": "classic"
    }

    apis = ["https://api.cobalt.tools/api/json", "https://co.wuk.sh/api/json"]

    for api in apis:
        try:
            response = requests.post(api, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                res = response.json()
                if "url" in res:
                    return jsonify({"success": True, "direct_url": res["url"]})
        except: continue

    return jsonify({"success": False, "error": "Servers busy, please wait 30 seconds."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
