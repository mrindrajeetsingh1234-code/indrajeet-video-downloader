import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚡ INFO FETCHING (Thumbnail, Title, Description ke liye)
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': ['player_client=android']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Unknown Title'),
                "thumb": info.get('thumbnail', ''),
                "description": info.get('description', ''),
                "qualities": ["1080p", "720p", "480p", "Audio (MP3)"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Info fetch failed: " + str(e)})

# ⚡ DOWNLOADER (Insta, FB, TikTok, YouTube sabke liye)
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'extractor_args': {'youtube': ['player_client=android']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info['formats'][-1]['url'] if 'formats' in info else None)
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            else:
                return jsonify({"success": False, "error": "Could not extract video."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
