from flask import Flask, render_template, request, send_file, jsonify
import subprocess, os, uuid

app = Flask(__name__)

DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/api/download")
def download_api():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    try:
        subprocess.run([
            "yt-dlp",
            url,
            "-f", "b",
            "-o", filepath,
            "--merge-output-format", "mp4",
            "--no-check-certificate",
            "--user-agent", "Mozilla/5.0"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except subprocess.CalledProcessError as e:
        err = e.stderr.decode()

        # Bot/JS block aaye to browser fallback
        if "not a bot" in err or "Sign in to confirm" in err or "JS runtime" in err:
            return jsonify({"fallback": "browser"}), 200

        return jsonify({"error": "Download failed: " + err}), 500

    if not os.path.exists(filepath):
        return jsonify({"fallback": "browser"}), 200

    response = send_file(filepath, as_attachment=True, download_name="video.mp4")

    try:
        os.remove(filepath)
    except:
        pass

    return response

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
