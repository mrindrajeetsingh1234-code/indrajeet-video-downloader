import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# yt-dlp ki strict configuration
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'format': 'best',
    'cookiefile': 'cookies.txt', # Yeh line cookies load karegi
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'cookiefile': 'cookies.txt'}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["Best Quality"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            else:
                return jsonify({"success": False, "error": "Extraction failed."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
