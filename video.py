import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER): os.makedirs(DOWNLOAD_FOLDER)

def get_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    }

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL(get_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Quality Extraction Logic
            formats = info.get('formats', [])
            res = sorted(list(set([f.get('height') for f in formats if f.get('height')])), reverse=True)
            qualities = [f"{r}p" for r in res if r >= 360] or ["Best Quality"]
            
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": info.get('thumbnail'),
                "qualities": qualities
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return jsonify({"success": True, "filename": os.path.basename(ydl.prepare_filename(info))})
    except Exception as e:
        return jsonify({"success": False, "error": "Server Busy/Blocked"})

@app.route('/files/<filename>')
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
