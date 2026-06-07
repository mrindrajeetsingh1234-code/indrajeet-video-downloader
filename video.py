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

# ⚡ STEP 1: VIDEO INFO
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True, 'no_warnings': True, 'noplaylist': True,
            'extract_flat': 'in_playlist',
            'extractor_args': {'youtube': ['player_client=ios,android,tv,web']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            thumb = info.get('thumbnail', '')
            formats = info.get('formats', [])
            live_res = {f.get('height') for f in formats if f.get('vcodec') != 'none' and f.get('height')}
            final_qualities = [f"{res}p" for res in sorted(list(live_res), reverse=True)[:4]]
            if not final_qualities: final_qualities = ["1080p", "720p", "480p"]
            final_qualities.append("Audio (MP3)")

            return jsonify({"success": True, "title": title, "thumb": thumb, "metadata": f"Title: {title}\nLink: {url}", "qualities": final_qualities})
    except:
        return jsonify({"success": True, "title": "YouTube Video", "thumb": "", "metadata": f"Link: {url}", "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]})

# ⚡ STEP 2: DIRECT FAST DOWNLOAD (V7 API COMPATIBLE)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # 'best' format direct stream uthane ke liye
            'format': 'best', 
            'extractor_args': {'youtube': ['player_client=android']}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Direct link find karna
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                # Agar direct URL nahi milta, toh best format ka link uthao
                video_url = info['formats'][-1]['url']
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            else:
                return jsonify({"success": False, "error": "Could not extract video stream."})

    except Exception as e:
        return jsonify({"success": False, "error": f"Direct Stream Failed: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), use_reloader=False)
