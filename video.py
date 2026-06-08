import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER): os.makedirs(DOWNLOAD_FOLDER)

# 🚀 Anti-Ban Settings (IP Block होने से बचाएगा)
def get_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        },
        # YouTube और Instagram को लगेगा मोबाइल से रिक्वेस्ट आ रही है
        'extractor_args': {'youtube': ['player_client=android,ios']}
    }

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "URL missing"})
    
    try:
        with yt_dlp.YoutubeDL(get_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Title और Thumbnail निकालना
            title = info.get('title') or info.get('fulltitle') or 'Video Ready for Download'
            thumb = info.get('thumbnail')
            if not thumb and info.get('thumbnails'):
                thumb = info['thumbnails'][-1]['url']
            
            # Quality लिस्ट निकालना
            formats = info.get('formats', [])
            res = sorted(list(set([f.get('height') for f in formats if f.get('height')])), reverse=True)
            qualities = [f"{r}p" for r in res if r >= 360] or ["Best Quality (MP4)"]
            qualities.append("Audio (MP3)")
            
            return jsonify({
                "success": True, 
                "title": title, 
                "thumb": thumb, 
                "qualities": qualities
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Server is Busy or Link is Protected."})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL(get_opts()) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.basename(ydl.prepare_filename(info))
            return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": "Download blocked by platform."})

@app.route('/files/<filename>')
def serve_file(filename):
    response = make_response(send_from_directory(DOWNLOAD_FOLDER, filename))
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/octet-stream"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
