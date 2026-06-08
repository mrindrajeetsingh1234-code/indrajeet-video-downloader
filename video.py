import os
import re
import yt_dlp
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# आपका पुराना फोल्डर वाला सिस्टम जो 100% काम करता था
DOWNLOAD_FOLDER = os.path.abspath("downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def get_safe_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo-bypass': True,
        'extractor_args': {'youtube': ['player_client=android']}, # रोबोट बैन से बचने के लिए
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
    }

@app.route('/')
def index():
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Backend is running!"

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL provided"})

    try:
        ydl_opts = get_safe_ydl_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 🔥 100% पक्का थंबनेल निकालने का लॉजिक
            thumb = info.get('thumbnail', '')
            if not thumb and info.get('thumbnails'):
                thumb = info['thumbnails'][-1]['url']

            # 🔥 सारी क्वालिटी निकालने का लॉजिक (वापस आ गया)
            formats = info.get('formats', [])
            live_resolutions = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    live_resolutions.add(f.get('height'))
            
            sorted_res = sorted(list(live_resolutions), reverse=True)
            qualities = []
            for res in sorted_res:
                if res >= 2160: qualities.append(f"4K ({res}p)")
                elif res >= 1080: qualities.append(f"HD ({res}p)")
                elif res >= 480: qualities.append(f"SD ({res}p)")
                else: qualities.append(f"Low ({res}p)")
            
            if not qualities:
                qualities = ["Best Quality (MP4)"]
            qualities.append("Audio (MP3)")

            return jsonify({
                "success": True, 
                "title": info.get('title', 'Video'), 
                "thumb": thumb,
                "qualities": qualities
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Link Protected or Invalid."})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = get_safe_ydl_opts()
        ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        ydl_opts['noplaylist'] = True

        if 'Audio' in quality or 'MP3' in quality:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        else:
            # वीडियो के लिए क्वालिटी सेट करना
            match = re.search(r'(\d+)p', quality)
            if match:
                h = match.group(1)
                ydl_opts['format'] = f'best[height<={h}][ext=mp4]/bestvideo[height<={h}]+bestaudio/best'
            else:
                ydl_opts['format'] = 'best[ext=mp4]/bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'

        # 🔥 वीडियो अब आपके सर्वर पर डाउनलोड होगी (पुराना और पक्का तरीका)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            output_path = ydl.prepare_filename(info)
            base, ext = os.path.splitext(output_path)
            final_file = base + '.mp3' if 'Audio' in quality else base + '.mp4'
            
        # डाउनलोड होने के बाद फाइल का नाम फ्रंटएंड को भेजना
        return jsonify({"success": True, "filename": os.path.basename(final_file)})
    except Exception as e:
        return jsonify({"success": False, "error": "Download Failed. Protected Link."})

# 🔥 वीडियो को यूज़र के कंप्यूटर में सीधा सेव करवाने का रूट
@app.route('/fetch_file/<path:filename>', methods=['GET'])
def fetch_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
