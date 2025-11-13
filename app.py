# app.py  (run on your PC for local testing)
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

ping_results = {}
last_update = None

@app.route("/")
def index():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT")
    return render_template(
        "index.html",
        results=ping_results,
        last_update=last_update or "Waiting for data...",
        current_time=current_time
    )

@app.route("/update", methods=["POST"])
def update():
    global ping_results, last_update
    data = request.get_json()
    if data and "results" in data:
        ping_results = data["results"]
        # EAT = UTC+3
        last_update = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S EAT")
        print(f"[LOCAL] Updated: {len(ping_results)} regions")
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    print("Local dashboard: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)