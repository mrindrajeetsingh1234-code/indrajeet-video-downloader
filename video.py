import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER): os.makedirs(DOWNLOAD_FOLDER)

# 🚀 Optimized Settings: बैन होने से बचने के लिए
def get_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'format': 'best',
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    }

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            # 🚀 info_dict को सीधे निकालें
            info = ydl.extract_info(url, download=False)
            
            # टाइटल निकालना
            title = info.get('title', 'Video Content')
            
            # थंबनेल निकालना
            thumb = info.get('thumbnail', '')
            if not thumb and info.get('thumbnails'): thumb = info['thumbnails'][-1]['url']
            
            # क्वालिटी लिस्ट बनाना (यह अब पक्का काम करेगा)
            formats = info.get('formats', [])
            res_set = set()
            for f in formats:
                if f.get('height'): res_set.add(f.get('height'))
            
            sorted_res = sorted(list(res_set), reverse=True)
            qualities = [f"{r}p" for r in sorted_res if r >= 360]
            if not qualities: qualities = ["Best Quality"]
            qualities.append("Audio (MP3)")

            return jsonify({
                "success": True,
                "title": title,
                "thumb": thumb,
                "qualities": qualities
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to fetch details. Try another link."})
