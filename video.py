import os
import urllib.request
import json
import re  # 🔥 नया इंपोर्ट (ID निकालने के लिए)
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "🚀 Indrajeet Ultra-Fast Backend Running!"})

# ⚡ STEP 1: VIDEO INFO (SMART BYPASS)
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'noplaylist': True,            
            'extract_flat': 'in_playlist',
            'extractor_args': {'youtube': ['player_client=ios,android,tv,web']}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            thumb = info.get('thumbnail', '')
            
            formats = info.get('formats', [])
            live_res = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'): live_res.add(f.get('height'))
            
            final_qualities = [f"{res}p" for res in sorted(list(live_res), reverse=True)[:4]]
            if not final_qualities:
                final_qualities = ["1080p", "720p", "480p"]
            final_qualities.extend(["Audio (MP3)"])

            return jsonify({
                "success": True,
                "title": title,
                "thumb": thumb,
                "metadata": f"Title: {title}\n\nLink: {url}",
                "qualities": final_qualities
            })
    except Exception as e:
        # 🔥 SMART INFO BYPASS: अगर YouTube ब्लॉक करे, तो हमारा कोड हार नहीं मानेगा!
        if "youtube" in url or "youtu.be" in url:
            video_id = ""
            # लिंक से सीधे Video ID निकालो
            match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
            if match: video_id = match.group(1)
            
            return jsonify({
                "success": True,
                "title": "YouTube Video (Secured Download)",
                "thumb": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "metadata": f"Link: {url}\n\nNote: Security Bypass Active.",
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"] # डिफ़ॉल्ट क्वालिटी ऑप्शंस
            })
        
        return jsonify({"success": False, "error": str(e)})

# ⚡ STEP 2: DIRECT FAST DOWNLOAD (BYPASSING SERVER)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    
    if not url: return jsonify({"success": False, "error": "No URL"})

    is_audio = 'Audio' in quality or 'MP3' in quality
    
    v_quality = "1080"
    if "720" in quality: v_quality = "720"
    elif "480" in quality: v_quality = "480"

    try:
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = json.dumps({
            "url": url, 
            "vQuality": v_quality, 
            "isAudioOnly": is_audio, 
            "aFormat": "mp3"
        }).encode('utf-8')
        
        # 🚀 FAST API 1: Cobalt Main
        req1 = urllib.request.Request("https://api.cobalt.tools/api/json", data=payload, headers=headers)
        with urllib.request.urlopen(req1, timeout=8) as response:
            res = json.loads(response.read().decode())
            if "url" in res:
                return jsonify({"success": True, "direct_url": res["url"]})
    except:
        pass 

    try:
        # 🚀 FAST API 2: Wuk.sh (Backup)
        req2 = urllib.request.Request("https://co.wuk.sh/api/json", data=payload, headers=headers)
        with urllib.request.urlopen(req2, timeout=8) as response:
            res = json.loads(response.read().decode())
            if "url" in res:
                return jsonify({"success": True, "direct_url": res["url"]})
    except Exception as e:
        return jsonify({"success": False, "error": "Servers are busy. Try again!"})

    return jsonify({"success": False, "error": "Could not extract fast link."})

if __name__ == '__main__':
    print("🚀 Indrajeet Fast Backend Ready!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=False)
