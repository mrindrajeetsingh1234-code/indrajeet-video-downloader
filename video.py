import os
import re
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Backend is running!"

def get_safe_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo-bypass': True,
        'extractor_args': {'youtube': ['player_client=android']},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
    }

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = get_safe_ydl_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 100% Working Thumbnail Logic
            thumb = info.get('thumbnail', '')
            if not thumb and 'thumbnails' in info and len(info['thumbnails']) > 0:
                thumb = info['thumbnails'][-1]['url']

            # Original Quality Logic Added Back
            formats = info.get('formats', [])
            live_resolutions = set()
            
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    live_resolutions.add(f.get('height'))
            
            sorted_res = sorted(list(live_resolutions), reverse=True)
            final_qualities = []
            
            for res in sorted_res:
                if res >= 2160: final_qualities.append(f"4K ({res}p)")
                elif res >= 1440: final_qualities.append(f"2K ({res}p)")
                elif res == 1080: final_qualities.append("Full HD (1080p)")
                elif res == 720: final_qualities.append("HD (720p)")
                elif res >= 144: final_qualities.append(f"{res}p")
            
            if not final_qualities:
                final_qualities = ["Best Available (HD)"]
                
            final_qualities.append("Audio (MP3)")

            return jsonify({
                "success": True, 
                "title": info.get('title', 'Video'), 
                "thumb": thumb,
                "qualities": final_qualities
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Platform Blocked or Private Video."})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'Best')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = get_safe_ydl_opts()
        
        if 'Audio' in quality or 'MP3' in quality:
            ydl_opts['format'] = 'bestaudio/best'
        else:
            match = re.search(r'(\d+)p', quality)
            if match:
                height = match.group(1)
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best'
            else:
                ydl_opts['format'] = 'best[ext=mp4]/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            link = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if link:
                return jsonify({"success": True, "direct_url": link})
            return jsonify({"success": False, "error": "Link Protected"})
    except Exception as e:
        return jsonify({"success": False, "error": "Try again, link protected."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
