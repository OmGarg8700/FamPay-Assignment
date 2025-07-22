from flask import Flask, jsonify, request
from connection import init_db
from service import get_videos_paginated

app = Flask(__name__)
init_db()

@app.route('/getData', methods=['GET'])
def getVideosData():
    try:
        page_no = int(request.args.get('pageNo', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({"error": "Invalid pageNo or limit"}), 400

    if page_no < 1 or limit < 1:
        return jsonify({"error": "pageNo and limit must be positive integers"}), 400

    response, code = get_videos_paginated(page_no, limit)
    return jsonify(response), code

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "isError": False,
        "message": "Server is Up and Running"
    }), 200

if __name__ == "__main__":
    port = 5000
    print(f"Server running on port {port}")
    app.run(host='0.0.0.0', port=port)