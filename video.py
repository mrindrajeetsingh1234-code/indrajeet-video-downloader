import os
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

# 🚀 एकदम तगड़ी yt-dlp सेटिंग (Instagram और YouTube Bypass के साथ)
def get_bypass_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo-bypass': True,
        'format': 'best',
        # YouTube को लगेगा कि Android और iOS ऐप से वीडियो देखा जा रहा है
        'extractor_args': {'youtube': ['player_client=ios,android']},
        # Instagram को लगेगा कि Safari ब्राउज़र (iPhone) से रिक्वेस्ट आ रही है
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
        }
    }

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = get_bypass_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_flat हटा दिया है ताकि थंबनेल और क्वालिटी की पूरी लिस्ट पक्का आए
            info = ydl.extract_info(url, download=False)
            
            # थंबनेल लॉजिक
            thumb = info.get('thumbnail', '')
            if not thumb and info.get('thumbnails'):
                thumb = info['thumbnails'][-1]['url']

            # क्वालिटी लॉजिक
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
        return jsonify({"success": False, "error": "Link Protected by Platform (IP Blocked)."})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = get_bypass_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # सीधा डायरेक्ट लिंक निकालेगा, सर्वर पर डाउनलोड नहीं करेगा (Time बचेगा)
            link = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if link:
                return jsonify({"success": True, "direct_url": link})
            return jsonify({"success": False, "error": "Direct Link Missing"})
    except Exception as e:
        return jsonify({"success": False, "error": "Download blocked by platform."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
