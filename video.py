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

# डाउनलोड किए गए वीडियो सेव करने के लिए फोल्डर
DOWNLOAD_FOLDER = os.path.abspath("downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 1. LIVE QUALITY EXTRACTOR (All Platforms Supported)
@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    try:
       YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'format': 'best',
    'extractor_args': {'youtube': ['player_client=android']},
    'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
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
                if res >= 2160:
                    final_qualities.append("4K (2160p)")
                elif res >= 1440:
                    final_qualities.append("2K (1440p)")
                elif res == 1080:
                    final_qualities.append("Full HD (1080p)")
                elif res == 720:
                    final_qualities.append("HD (720p)")
                elif res >= 144:
                    final_qualities.append(f"{res}p")

            # अगर प्लेटफॉर्म (जैसे TikTok) हाइट नहीं देता, तो डिफ़ॉल्ट ऑप्शन भेजें
            if not final_qualities:
                final_qualities = ["Best Available (.mp4)", "Audio (.mp3)"]
            else:
                final_qualities.append("Best Available")
                final_qualities.append("Audio (MP3)")

            return jsonify({
                "success": True,
                "title": info.get('title', 'Unknown Title'),
                "thumb": info.get('thumbnail', ''),
                "qualities": final_qualities
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 2. 🚀 HIGH-SPEED DOWNLOADER LOGIC
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    try:
        # ⚡ SPEED HACKS ADDED HERE ⚡
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'concurrent_fragment_downloads': 10, # 🚀 10 हिस्सों में एक साथ डाउनलोड (IDM Style)
            'http_chunk_size': 10485760,         # 🚀 10MB के चंक्स बनाएगा
            'retries': 5,                        # 🚀 फेल होने पर 5 बार खुद कोशिश करेगा
            'nocheckcertificate': True
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


# 3. FILE SENDER ROUTE
@app.route('/fetch_file/<path:filename>', methods=['GET'])
def fetch_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8888)
