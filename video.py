import yt_dlp
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🚀 परमानेंट yt-dlp सेटिंग्स (बिना किसी API के)
def get_ydl_opts():
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'format': 'best',
        'nocheckcertificate': True,
        'geo-bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    }
    # अगर आपने cookies.txt फाइल डाली है, तो यह खुद उसे इस्तेमाल कर लेगा
    if os.path.exists('cookies.txt'):
        opts['cookiefile'] = 'cookies.txt'
    return opts

@app.route('/')
def index():
    # आपकी वेबसाइट दिखाने के लिए
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Backend is running permanently! Please add index.html to your folder."

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL provided"})

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumb": info.get('thumbnail', ''),
                "qualities": ["Best Quality"]
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Cannot fetch video info. It might be private or protected."})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL provided"})

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # सिर्फ डायरेक्ट लिंक निकाल रहा है, ताकि सर्वर पर लोड न पड़े
            video_url = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            else:
                return jsonify({"success": False, "error": "Direct download link not found."})
    except Exception as e:
        return jsonify({"success": False, "error": "Platform blocked the download. Try another video."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
