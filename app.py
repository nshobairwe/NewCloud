# app.py (on Render – receives data)
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Global storage
ping_results = {}
last_update = None

@app.route("/")
def index():
    global last_update
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT")
    return render_template(
        "index.html",
        results=ping_results,
        interval=10,
        current_time=current_time,
        last_update=last_update
    )

# API endpoint to receive ping results
@app.route("/update", methods=["POST"])
def update():
    global ping_results, last_update
    data = request.get_json()
    if data and "results" in data:
        ping_results = data["results"]
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT")
        print(f"[CLOUD] Received update from local: {len(ping_results)} regions")
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)