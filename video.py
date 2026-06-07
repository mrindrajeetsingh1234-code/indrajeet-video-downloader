import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

APIS = [
    "https://api.cobalt.tools/api/json",
    "https://co.wuk.sh/api/json"
]

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False})

    for api in APIS:
        try:
            # Cobalt/Wuk API का फॉर्मेट JSON होता है
            resp = requests.post(api, json={"url": url}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # यहाँ 'filename' को 'title' में मैप करना जरूरी है
                return jsonify({
                    "success": True,
                    "title": data.get("filename") or data.get("title") or "Video",
                    "thumb": data.get("thumbnail") or "",
                    "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
                })
        except: continue
    return jsonify({"success": False, "error": "All APIs down"})

@app.route('/download', methods=['POST'])
def download_video():
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
                data = resp.json()
                if "url" in data:
                    return jsonify({"success": True, "direct_url": data["url"]})
        except: continue
        
    return jsonify({"success": False, "error": "Traffic high, try again!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
