import os
import json
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Cobalt Multi-Server Backend is Running!"})

@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    # वेबसाइट को फ़ास्ट रखने के लिए डिफ़ॉल्ट इन्फो
    return jsonify({
        "success": True,
        "title": "Video Ready To Download",
        "thumb": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop",
        "qualities": ["1080p Full HD (MP4)", "720p HD (MP4)", "Audio (MP3)"]
    })

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    is_audio = 'Audio' in quality or 'MP3' in quality
    
    payload = {
        "url": url,
        "isAudioOnly": is_audio,
        "aFormat": "mp3" if is_audio else "best",
        "vQuality": "1080" if "1080" in quality else "720"
    }
    
    # 🚀 असली ब्राउज़र वाला हेडर ताकि API ब्लॉक न करे
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    # 🚀 Multi-Server Fallback: अगर एक सर्वर बिजी है तो दूसरे पर जाएगा
    COBALT_SERVERS = [
        "https://api.cobalt.tools/api/json",
        "https://co.wuk.sh/api/json",
        "https://api.cobalt.ac/api/json"
    ]

    last_error = "All API Servers are currently busy. Please try after 1 minute."

    for api_url in COBALT_SERVERS:
        try:
            req = urllib.request.Request(api_url, data=json.dumps(payload).encode(), headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode())
                
                if res_data.get("status") in ["redirect", "stream", "success"]:
                    return jsonify({"success": True, "direct_url": res_data.get("url")})
                else:
                    last_error = res_data.get("text", "API Error")
        except Exception as e:
            continue  # 👈 अगर सर्वर बिजी है या फेल हुआ, तो कोड रुकेगा नहीं, अगले सर्वर को ट्राई करेगा!

    # अगर किस्मत बहुत ही खराब हुई और तीनों सर्वर एक साथ बिजी निकले
    return jsonify({"success": False, "error": last_error})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
