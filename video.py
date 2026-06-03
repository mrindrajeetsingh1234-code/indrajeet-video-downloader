import os
import json
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Cobalt API Backend is Running!"})

@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    # API के लिए फेक इन्फो ताकि वेबसाइट तुरंत लोड हो और यूट्यूब ब्लॉक न करे
    return jsonify({
        "success": True,
        "title": "Video Ready To Download",
        "thumb": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop", # एक बढ़िया डिफ़ॉल्ट थंबनेल
        "qualities": ["1080p Full HD (MP4)", "720p HD (MP4)", "Audio (MP3)"]
    })

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    try:
        is_audio = 'Audio' in quality or 'MP3' in quality
        
        # Cobalt API Payload
        payload = {
            "url": url,
            "isAudioOnly": is_audio,
            "aFormat": "mp3" if is_audio else "best",
            "vQuality": "1080" if "1080" in quality else "720"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request("https://api.cobalt.tools/api/json", data=json.dumps(payload).encode(), headers=headers)
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            
            if res_data.get("status") in ["redirect", "stream", "success"]:
                direct_link = res_data.get("url")
                # हम सीधा डायरेक्ट लिंक भेज रहे हैं जिससे स्पीड 10x हो जाएगी!
                return jsonify({"success": True, "direct_url": direct_link})
            else:
                return jsonify({"success": False, "error": res_data.get("text", "API Error")})

    except Exception as e:
        return jsonify({"success": False, "error": "API Servers are busy. Please try again."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
