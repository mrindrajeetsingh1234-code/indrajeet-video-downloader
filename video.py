import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
# CORS(app) बहुत जरूरी है ताकि आप कंप्यूटर से भी इसे चला सकें
CORS(app) 

@app.route('/')
def index():
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Backend is running!"

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        # extract_flat: True से लोडिंग स्पीड 10x तेज हो जाती है
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            thumb = info.get('thumbnail', '')
            if not thumb and 'thumbnails' in info and len(info['thumbnails']) > 0:
                thumb = info['thumbnails'][-1]['url']

            return jsonify({
                "success": True, 
                "title": info.get('title', 'Video'), 
                "thumb": thumb
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Platform Blocked or Private Video."})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best[ext=mp4]/best',
            'extractor_args': {'youtube': ['player_client=android']},
            'nocheckcertificate': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            link = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if link:
                return jsonify({"success": True, "direct_url": link})
            return jsonify({"success": False, "error": "Link Protected"})
    except Exception as e:
        return jsonify({"success": False, "error": "Try again, link protected."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
