import yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

# इसमें हमने एक बहुत ही बेसिक 'User-Agent' रोटेशन और 'Proxy' लगाने का रास्ता छोड़ दिया है
def get_ydl_opts():
    return {
        'quiet': True,
        'format': 'best',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            # यह कमांड सर्वर को 'इंसान' दिखाने के लिए है
            info = ydl.extract_info(url, download=False)
            link = info.get('url') or info.get('formats')[-1]['url']
            return jsonify({"success": True, "direct_url": link})
    except Exception as e:
        return jsonify({"success": False, "error": "IP Blocked by Instagram."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
