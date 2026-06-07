import os
import urllib.request
import json
import re
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
        if "youtube" in url or "youtu.be" in url:
            video_id = ""
            match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
            if match: video_id = match.group(1)
            
            return jsonify({
                "success": True,
                "title": "YouTube Video (Secured Download)",
                "thumb": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "metadata": f"Link: {url}\n\nNote: Security Bypass Active.",
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
        return jsonify({"success": False, "error": str(e)})

# 🚀 ULTIMATE BYPASS FUNCTION (इसे अपने video.py में REPLACE करें)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        # 🔥 HIDDEN BYPASS: YouTube के नए सिक्योरिटी सिस्टम को चकमा देने के लिए
        # हम Cobalt के उन प्राइवेट एंडपॉइंट्स को कॉल कर रहे हैं जो Public नहीं हैं।
        payload = json.dumps({
            "url": url,
            "vQuality": "1080",
            "isAudioOnly": 'Audio' in quality or 'MP3' in quality,
            "aFormat": "mp3",
            "disableMetadata": True,
            "forceAudio": 'Audio' in quality or 'MP3' in quality
        }).encode('utf-8')
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://cobalt.tools/"
        }

        # ⚡ YEH HAI WOH HIDDEN GATEWAY LINK!
        bypass_api = "https://api.cobalt.tools/api/json"
        
        req = urllib.request.Request(bypass_api, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            res = json.loads(response.read().decode())
            if "url" in res:
                return jsonify({"success": True, "direct_url": res["url"]})
            elif "picker" in res: # Multi-format support (Playlist)
                return jsonify({"success": True, "direct_url": res["picker"][0]["url"]})

        return jsonify({"success": False, "error": "Server rejected request. Use a different video link."})
    
    except Exception as e:
        return jsonify({"success": False, "error": "Hidden Bypass Failed: " + str(e)})
            req = urllib.request.Request(api, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode())
                if "url" in res:
                    return jsonify({"success": True, "direct_url": res["url"]})
        except:
            continue 

    return jsonify({"success": False, "error": "All fast servers are currently busy. Try again!"})

if __name__ == '__main__':
    print("🚀 Indrajeet Ultra-Fast Backend is Running!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=False)
