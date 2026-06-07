import yt_dlp
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Cookies file ka path
COOKIE_FILE = 'cookies.txt'

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        # Simple yt-dlp config
        ydl_opts = {
            'quiet': True,
            'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
            'format': 'best',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info.get('formats')[-1]['url'] if 'formats' in info else None)
            
            if video_url:
                return jsonify({"success": True, "direct_url": video_url})
            return jsonify({"success": False, "error": "Link nahi mila"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # PORT environment variable se le rahe hain, ye best practice hai
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
