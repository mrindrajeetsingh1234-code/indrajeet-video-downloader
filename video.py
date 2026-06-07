import urllib.request
import json
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚡ STEP 1: SMART INFO (थंबनेल के लिए भी बाईपास इस्तेमाल किया)
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        # थंबनेल और नाम के लिए Cobalt API का इस्तेमाल करें (क्योंकि yt-dlp ब्लॉक हो रहा है)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = json.dumps({"url": url}).encode('utf-8')
        
        req = urllib.request.Request("https://api.cobalt.tools/api/json", data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode())
            
            # अगर Cobalt से जानकारी मिल गई
            return jsonify({
                "success": True,
                "title": res.get("filename", "YouTube Video"),
                "thumb": res.get("thumbnail", ""),
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
    except:
        return jsonify({"success": False, "error": "Could not fetch info. Try another link."})

# ⚡ STEP 2: HYBRID DOWNLOAD (Cobalt Bypass)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    v_quality = "1080"
    if "720" in quality: v_quality = "720"
    elif "480" in quality: v_quality = "480"

    payload = json.dumps({
        "url": url,
        "videoQuality": v_quality,
        "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
        "audioFormat": "mp3"
    }).encode('utf-8')
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    # API List
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

    return jsonify({"success": False, "error": "Servers are busy. Try after 10 seconds."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)\';[p
