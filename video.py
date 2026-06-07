import yt_dlp
import requests
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# पक्का करें कि cookies.txt आपके फोल्डर में है
COOKIE_PATH = 'cookies.txt' 

YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'format': 'best',
    'nocheckcertificate': True,
    'geo-bypass': True,
    'cookiefile': COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
}

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    # कोशिश 1: yt-dlp (Cookies के साथ)
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
    except Exception as e:
        print(f"yt-dlp failed, switching to API: {e}")

    # कोशिश 2: अगर yt-dlp फेल हुआ, तो Cobalt API से निकालो
    try:
        resp = requests.post("https://api.cobalt.tools/api/json", json={"url": url}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if "url" in data:
                return jsonify({"success": True, "direct_url": data["url"]})
    except:
        pass

    return jsonify({"success": False, "error": "Video is protected or restricted. Try a public video."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
