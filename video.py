import os
import re
import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "High-Speed Video Downloader Backend is Running!",
        "routes": ["/check_info", "/download", "/fetch_file"]
    })

DOWNLOAD_FOLDER = os.path.abspath("downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    try:
        # 🚀 लेटेस्ट बायपास: Android और iOS क्लाइंट (बिना हेडर क्लैश के)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': ['player_client=android,ios']
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            live_resolutions = set()
            
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    live_resolutions.add(f.get('height'))
            
            sorted_res = sorted(list(live_resolutions), reverse=True)
            final_qualities = []
            
            for res in sorted_res:
                if res >= 2160: final_qualities.append("4K (2160p)")
                elif res >= 1440: final_qualities.append("2K (1440p)")
                elif res == 1080: final_qualities.append("Full HD (1080p)")
                elif res == 720: final_qualities.append("HD (720p)")
                elif res >= 144: final_qualities.append(f"{res}p")
            
            final_qualities.append("Best Available")
            final_qualities.append("Audio (MP3)")

            if not final_qualities or len(final_qualities) == 2:
                final_qualities = ["Best Available (.mp4)", "Audio (.mp3)"]

            return jsonify({
                "success": True,
                "title": info.get('title', 'Unknown Title'),
                "thumb": info.get('thumbnail', ''),
                "qualities": final_qualities
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    try:
        # 🚀 डाउनलोड के लिए भी सेम लेटेस्ट बायपास
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': ['player_client=android,ios']
            }
        }

        if 'Audio' in quality or 'MP3' in quality:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if 'Best' in quality:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                match = re.search(r'(\d+)p', quality)
                if match:
                    height = match.group(1)
                    ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

            ydl_opts['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            output_path = ydl.prepare_filename(info)
            base, ext = os.path.splitext(output_path)

            if 'Audio' in quality or 'MP3' in quality:
                final_file = base + '.mp3'
            else:
                final_file = base + '.mp4'

        return jsonify({"success": True, "filename": os.path.basename(final_file)})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/fetch_file/<path:filename>', methods=['GET'])
def fetch_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
