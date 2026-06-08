import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 3 अलग-अलग APIs का पूल (अगर एक बिजी है, तो दूसरी काम करेगी)
APIS = [
    "https://api.cobalt.tools/api/json", 
    "https://snap-save.com/api/v1/download",
]

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    # रोटेशन लॉजिक: एक बार API-1 से पूछो, फेल हो तो API-2 से
    for api_url in APIS:
        try:
            response = requests.post(api_url, json={"url": url}, timeout=10)
            if response.status_code == 200:
                return jsonify({"success": True, "direct_url": response.json().get('url')})
        except:
            continue
    return jsonify({"success": False, "error": "All APIs are busy. Try again."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
