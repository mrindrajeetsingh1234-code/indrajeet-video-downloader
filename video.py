import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER): os.makedirs(DOWNLOAD_FOLDER)

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            res = sorted(list(set([f.get('height') for f in formats if f.get('height')])), reverse=True)
            qualities = [f"{r}p" for r in res if r >= 360] or ["Best Quality"]
            qualities.append("Audio (MP3)")
            return jsonify({"success": True, "title": info.get('title'), "thumb": info.get('thumbnail'), "qualities": qualities})
    except: return jsonify({"success": False, "error": "Invalid Link"})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        ydl_opts = {'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'), 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return jsonify({"success": True, "filename": os.path.basename(ydl.prepare_filename(info))})
    except: return jsonify({"success": False, "error": "Server Busy"})

@app.route('/files/<filename>')
def serve_file(filename):
    response = make_response(send_from_directory(DOWNLOAD_FOLDER, filename))
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
