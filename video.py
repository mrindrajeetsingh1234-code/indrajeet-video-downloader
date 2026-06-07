import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Stealth mode configuration
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'format': 'best',
    'nocheckcertificate': True,
    'geo-bypass': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["Best Quality"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": f"Info Failed: {str(e)}"})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract direct URL
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                # Agar direct url nahi mila, toh formats list mein se best wala uthao
                video_url = info['formats'][-1].get('url')
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            else:
                return jsonify({"success": False, "error": "No direct link found."})
    except Exception as e:
        # Yahan tumhare logs mein asli error dikhega
        print(f"DEBUG ERROR: {str(e)}") 
        return jsonify({"success": False, "error": "Download failed. Link expired or protected."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
