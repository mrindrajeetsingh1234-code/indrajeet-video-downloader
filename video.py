import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. Headers (इन्हें बदलना बहुत जरूरी है)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

APIS = [
    "https://api.cobalt.tools/api/json",
    "https://co.wuk.sh/api/json",
    "https://cobalt.qewertyy.dev/api/json"
]

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL provided"})

    for api in APIS:
        try:
            # 'headers' जोड़ना सबसे जरूरी काम था
            resp = requests.post(api, json={"url": url}, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                return jsonify({
                    "success": True,
                    "title": data.get("filename") or data.get("title") or "Video",
                    "thumb": data.get("thumbnail") or "",
                    "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
                })
        except: continue
    
    return jsonify({"success": False, "error": "Server connection failed"})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    
    payload = {
        "url": url,
        "videoQuality": "720" if "720" in quality else "1080",
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3"
    }

    for api in APIS:
        try:
            # यहाँ भी 'headers' और 'payload' का सही स्ट्रक्चर है
            resp = requests.post(api, json=payload, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "url" in data:
                    return jsonify({"success": True, "direct_url": data["url"]})
        except: continue
        
    return jsonify({"success": False, "error": "Traffic high, try again!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
