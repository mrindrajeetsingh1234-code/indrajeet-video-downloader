import os
import re
import json
import urllib.request
import yt_dlp
import io
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = os.path.abspath("downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Indrajeet Pro Backend Running! (Fast API + OEmbed)"})

@app.route('/check_info', methods=['POST'])
def check_info():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"})

    is_youtube = 'youtube.com' in url or 'youtu.be' in url

    try:
        # Step 1: Try normal yt-dlp first
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {'youtube': ['player_client=android,web']}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown Title')
            thumb = info.get('thumbnail', '')
            description = info.get('description', '')
            tags = info.get('tags', [])
            tags_str = " ".join([f"#{t}" for t in tags]) if tags else ""
            
            formats = info.get('formats', [])
            live_res = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    live_res.add(f.get('height'))
            
            sorted_res = sorted(list(live_res), reverse=True)
            final_qualities = []
            for res in sorted_res:
                if res >= 2160: final_qualities.append("4K (2160p)")
                elif res >= 1440: final_qualities.append("2K (1440p)")
                elif res == 1080: final_qualities.append("Full HD (1080p)")
                elif res == 720: final_qualities.append("HD (720p)")
                elif res >= 144: final_qualities.append(f"{res}p")
            
            final_qualities.extend(["Best Available", "Audio (MP3)"])
            if len(final_qualities) == 2: final_qualities = ["Best Available (.mp4)", "Audio (.mp3)"]

            full_metadata = f"Title: {title}\n\nTags: {tags_str}\n\nDescription: {description[:300]}..."

            return jsonify({
                "success": True,
                "title": title,
                "thumb": thumb,
                "metadata": full_metadata,
                "qualities": final_qualities
            })
            
    except Exception as e:
        # 🚀 STEP 2 (MASTERPLAN): अगर YouTube ने Block किया, तो Official API से असली डेटा निकालेंगे!
        if is_youtube:
            try:
                oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
                req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    yt_data = json.loads(response.read().decode())
                    real_title = yt_data.get("title", "YouTube Video")
                    real_thumb = yt_data.get("thumbnail_url", "")
                    author = yt_data.get("author_name", "")
                    
                    # कॉपी बॉक्स के लिए शानदार फॉर्मेट
                    meta = f"Title: {real_title}\nChannel: {author}\nLink: {url}\n\n#YouTube #Video #Download"
                    
                    return jsonify({
                        "success": True,
                        "title": real_title,
                        "thumb": real_thumb, # 100% असली थंबनेल
                        "metadata": meta,    # 100% असली टाइटल
                        "qualities": ["1080p Full HD (MP4)", "720p HD (MP4)", "Audio (MP3)"]
                    })
            except Exception as ex:
                pass

        return jsonify({"success": False, "error": "Server blocked by YouTube. Please try again."})

# 🚀 NEW: थंबनेल को डिवाइस में सेव करने वाला जुगाड़ (CORS Bypass)
@app.route('/download_thumb', methods=['POST'])
def download_thumb():
    img_url = request.json.get('img_url')
    if not img_url: return jsonify({"success": False, "error": "No image URL"})
    try:
        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
            return send_file(io.BytesIO(image_data), mimetype='image/jpeg', as_attachment=True, download_name='Indrajeet_Thumbnail.jpg')
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '')
    if not url: return jsonify({"success": False, "error": "No URL"})

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'concurrent_fragment_downloads': 5,
            'extractor_args': {'youtube': ['player_client=android,web']}
        }
        
        if 'Audio' in quality or 'MP3' in quality:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        else:
            match = re.search(r'(\d+)p', quality)
            if match:
                h = match.group(1)
                ydl_opts['format'] = f'bestvideo[height<={h}]+bestaudio/best'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            output_path = ydl.prepare_filename(info)
            base, ext = os.path.splitext(output_path)
            final_file = base + '.mp3' if ('Audio' in quality or 'MP3' in quality) else base + '.mp4'

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
