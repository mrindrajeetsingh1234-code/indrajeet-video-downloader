import yt_dlp
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_ydl_opts():
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        # 🚀 SPEED FIX: यह हमेशा MP4 फॉर्मेट और सबसे बेस्ट क्वालिटी उठाएगा
        'format': 'best[ext=mp4]/best', 
        'nocheckcertificate': True,
        'geo-bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
    }
    if os.path.exists('cookies.txt'):
        opts['cookiefile'] = 'cookies.txt'
    return opts

@app.route('/')
def index():
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Backend is running!"

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL provided"})

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 🚀 THUMBNAIL FIX: सबसे हाई क्वालिटी का थंबनेल निकालने का लॉजिक
            thumb_url = ""
            if 'thumbnails' in info and len(info['thumbnails']) > 0:
                thumb_url = info['thumbnails'][-1]['url'] # लिस्ट का आखिरी थंबनेल सबसे HD होता है
            elif info.get('thumbnail'):
                thumb_url = info.get('thumbnail')
            
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": thumb_url,
                "qualities": ["High Quality (MP4)"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Cannot fetch video info. It might be private or protected."})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL provided"})

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_url = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            else:
                return jsonify({"success": False, "error": "Direct link not found."})
    except Exception as e:
        return jsonify({"success": False, "error": "Platform blocked the download. Try another video."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
