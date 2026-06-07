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
            'nocheckcertificate': True, 
            'geo_bypass': True,
            'noplaylist': True,
            'concurrent_fragment_downloads': 10, 
            'retries': 5, 
            'extractor_args': {
                'youtube': ['player_client=ios,android,tv,web']
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        # 🍪 ऑटोमैटिक कुकीज़ डिटेक्शन
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = 'cookies.txt'

        # 🔥 SMART FORMAT SELECTOR (इस एरर का पक्का इलाज)
        if 'Audio' in quality or 'MP3' in quality:
            ydl_opts['format'] = 'ba/b' # (Best Audio या जो भी बेस्ट मिले)
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        elif quality and 'p' in quality: 
            # अगर आपने 1080p या 720p सेलेक्ट किया है
            res = quality.replace('p', '')
            ydl_opts['format'] = f'bv*[height<={res}]+ba/b[height<={res}]/b'
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            # Default (Best Available) - 'bv*+ba/b' कभी एरर नहीं देगा!
            ydl_opts['format'] = 'bv*+ba/b' 
            ydl_opts['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_file = ydl.prepare_filename(info)
            if 'Audio' in quality or 'MP3' in quality: final_file = os.path.splitext(final_file)[0] + '.mp3'
        
        return jsonify({"success": True, "filename": os.path.basename(final_file)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
