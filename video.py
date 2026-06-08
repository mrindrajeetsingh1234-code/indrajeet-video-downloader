import yt_dlp
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🚀 No-Cookie, High-Stealth yt-dlp Settings
def get_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'format': 'best[ext=mp4]/best', # हमेशा MP4 निकालने की कोशिश करेगा
        'nocheckcertificate': True,
        'geo-bypass': True,
        'http_headers': {
            # iPhone का User-Agent ताकि सर्वर को लगे कि असली इंसान है
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
    }

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
            
            # Thumbnail Logic
            thumb_url = ""
            if 'thumbnails' in info and len(info['thumbnails']) > 0:
                thumb_url = info['thumbnails'][-1]['url']
            elif info.get('thumbnail'):
                thumb_url = info.get('thumbnail')
            
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": thumb_url,
                "qualities": ["Best Quality (MP4)"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Info failed. Platform blocked the request."})

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
        return jsonify({"success": False, "error": "Download blocked by platform. Try another public video."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
