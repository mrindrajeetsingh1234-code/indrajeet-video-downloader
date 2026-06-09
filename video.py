import os
import yt_dlp
import requests
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER): os.makedirs(DOWNLOAD_FOLDER)

def get_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'format': 'bestvideo+bestaudio/best/all',
        
        # 🔥 FIX: यह लाइन किसी भी स्पेशल कैरेक्टर, इमोजी या चाइनीज़ टेक्स्ट को URL ब्लॉक करने से रोकेगी
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'IVD_%(id)s.%(ext)s'),
        'restrictfilenames': True, 
        
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': '*/*'
        }
    }

@app.route('/proxy_thumb')
def proxy_thumb():
    img_url = request.args.get('url')
    if not img_url: return "", 400
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(img_url, headers=headers, timeout=10)
        response = make_response(r.content)
        response.headers['Content-Type'] = r.headers.get('Content-Type', 'image/jpeg')
        return response
    except:
        return "", 500

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "URL missing"})
    
    try:
        with yt_dlp.YoutubeDL(get_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title') or info.get('description') or 'Video Ready for Download'
            
            thumb = info.get('thumbnail')
            if not thumb and info.get('thumbnails'):
                thumb = info['thumbnails'][-1]['url']
            
            formats = info.get('formats', [])
            res = sorted(list(set([f.get('height') for f in formats if f.get('height')])), reverse=True)
            qualities = [f"{r}p" for r in res if r >= 360] or ["Best Quality (MP4)"]
            qualities.append("Audio (MP3)")
            
            return jsonify({"success": True, "title": title, "thumb": thumb, "qualities": qualities})
    except Exception as e:
        error_msg = str(e)
        if "cookies" in error_msg.lower():
            return jsonify({"success": False, "error": "इस प्लेटफॉर्म के लिए Server पर Cookies की ज़रूरत है।"})
        return jsonify({"success": False, "error": error_msg})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL(get_opts()) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.basename(ydl.prepare_filename(info))
            return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/files/<filename>')
def serve_file(filename):
    response = make_response(send_from_directory(DOWNLOAD_FOLDER, filename))
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/octet-stream"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
