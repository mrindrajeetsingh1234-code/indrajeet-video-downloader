import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 🚀 /keep-alive: सर्वर को जगाने के लिए एक छोटा सा एंडपॉइंट
@app.route('/keep-alive', methods=['GET'])
def keep_alive():
    return "I am awake!", 200

@app.route('/check_info', methods=['POST'])
def check_info():
    url = request.json.get('url')
    try:
        ydl_opts = {'quiet': True, 'extractor_args': {'youtube': ['player_client=android']}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True, 
                "title": info.get('title'), 
                "thumb": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid Link"})

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        ydl_opts = {'quiet': True, 'format': 'best', 'extractor_args': {'youtube': ['player_client=android']}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            link = info.get('url') or info.get('formats')[-1]['url']
            return jsonify({"success": True, "direct_url": link})
    except Exception as e:
        return jsonify({"success": False, "error": "Protected Link"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
