import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# फाइल सेव करने की जगह
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "URL missing"})
    
    try:
        # User-Agent को और बेहतर बनाया है ताकि बैन न हो
        ydl_opts = {
            'quiet': True,
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True, 
                "title": info.get('title', 'Video'), 
                "thumb": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Platform Blocked"})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "URL missing"})
    
    try:
        # 'best' क्वालिटी के लिए और सर्वर क्रैश न हो इसलिए 'noplaylist'
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.basename(ydl.prepare_filename(info))
            return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": "Server Busy or Link Protected"})

# फाइल डाउनलोड करने का लिंक (डायरेक्ट लिंक)
@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    # threaded=True बहुत ज़रूरी है
    app.run(host='0.0.0.0', port=5000, threaded=True)
