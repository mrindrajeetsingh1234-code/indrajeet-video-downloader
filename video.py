import urllib.request
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚡ SMART INFO FETCHER (Multiple APIs ke saath)
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    # जिन सर्वर्स पर हमें चेक करना है
    apis = ["https://co.wuk.sh/api/json", "https://cobalt.qewertyy.dev/api/json"]
    payload = json.dumps({"url": url}).encode('utf-8')
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    for api in apis:
        try:
            req = urllib.request.Request(api, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                res = json.loads(response.read().decode())
                # अगर सही रिस्पॉन्स मिला
                return jsonify({
                    "success": True,
                    "title": res.get("filename", "YouTube Video"),
                    "thumb": res.get("thumbnail", ""),
                    "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
                })
        except:
            continue
            
    return jsonify({"success": False, "error": "All Info Servers Busy. Try again!"})

# ⚡ SMART DOWNLOADER
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    payload = json.dumps({
        "url": url,
        "videoQuality": "1080" if "720" not in quality else "720",
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3"
    }).encode('utf-8')
    
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    apis = ["https://co.wuk.sh/api/json", "https://cobalt.qewertyy.dev/api/json"]

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
    app.run(host='0.0.0.0', port=5000)
