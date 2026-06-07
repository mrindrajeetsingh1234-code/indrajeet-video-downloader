import os
import urllib.request
import json
import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Indrajeet Pro Backend Running!"})

@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True, 
            'nocheckcertificate': True, 
            'geo_bypass': True,
            'noplaylist': True,
            'concurrent_fragment_downloads': 10, 
            'retries': 5, 
            # DHYAN DEIN: Chrome browser wali line yahan se hata di gayi hai
            'extractor_args': {
                'youtube': ['player_client=ios,android,tv,web']
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        # Ye line aapki upload ki hui cookies.txt ko apne aap use kar legi
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = 'cookies.txt'

        # 🍪 अगर आपने cookies.txt फाइल बनाई है, तो यह ऑटोमैटिक उसे यूज़ कर लेगा (बिना क्रैश हुए)
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            
            formats = info.get('formats', [])
            live_res = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'): live_res.add(f.get('height'))
            
            final_qualities = [f"{res}p" for res in sorted(list(live_res), reverse=True)]
            final_qualities.extend(["Best Available", "Audio (MP3)"])

            return jsonify({
                "success": True,
                "title": title,
                "thumb": info.get('thumbnail', ''),
                "metadata": f"Title: {title}\n\nLink: {url}",
                "qualities": final_qualities
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True, 
            'nocheckcertificate': True, 
            'geo_bypass': True,
            'noplaylist': True,
            'concurrent_fragment_downloads': 10, # 🚀 SUPER SPEED: 20 मिनट की वीडियो को 10 हिस्सों में एक साथ डाउनलोड करेगा!
            'retries': 5, # अगर इंटरनेट बीच में कटा, तो फेल नहीं होगा, 5 बार दोबारा कोशिश करेगा
            'extractor_args': {
                'youtube': ['player_client=ios,android,tv,web']
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        # 🍪 ऑटोमैटिक कुकीज़ डिटेक्शन
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = 'cookies.txt'

        if 'Audio' in quality or 'MP3' in quality:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_file = ydl.prepare_filename(info)
            if 'Audio' in quality or 'MP3' in quality: final_file = os.path.splitext(final_file)[0] + '.mp3'
        
        return jsonify({"success": True, "filename": os.path.basename(final_file)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 🔥 YOUTUBE & TIKTOK SPECIAL BOX BYPASS (CORS KILLER) 🔥
@app.route('/cobalt_bypass', methods=['POST'])
def cobalt_bypass():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})
    
    try:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = json.dumps({"url": url, "vQuality": "1080", "isAudioOnly": False, "aFormat": "mp3"}).encode('utf-8')
        
        # कोशिश 1: पहला API
        try:
            req1 = urllib.request.Request("https://api.cobalt.tools/api/json", data=payload, headers=headers)
            with urllib.request.urlopen(req1, timeout=10) as response:
                res = json.loads(response.read().decode())
                if "url" in res: return jsonify({"success": True, "url": res["url"]})
        except: pass
        
        # कोशिश 2: अगर पहला फेल हुआ तो दूसरा API
        req2 = urllib.request.Request("https://co.wuk.sh/api/json", data=payload, headers=headers)
        with urllib.request.urlopen(req2, timeout=15) as response:
            res = json.loads(response.read().decode())
            if "url" in res: return jsonify({"success": True, "url": res["url"]})
                
        return jsonify({"success": False, "error": "Servers Busy"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/fetch_file/<path:filename>', methods=['GET'])
def fetch_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    print("🚀 Indrajeet SPEED Backend is Running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=False)
