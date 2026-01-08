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
        result = subprocess.run([
            "yt-dlp",
            url,
            "-f", "b",
            "-o", filepath,
            "--merge-output-format", "mp4",
            "--no-check-certificate",
            "--user-agent", "Mozilla/5.0",
            "--js-runtimes", "deno"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("Download STDOUT:", result.stdout.decode())
        print("Download STDERR:", result.stderr.decode())

    except subprocess.CalledProcessError as e:
        err = e.stderr.decode()

        # Agar bot verification aaye, to server download skip karke browser fallback allow karo
        if "not a bot" in err or "Sign in to confirm" in err or "JS runtime" in err:
            return jsonify({
                "error": "Shorts server download blocked. Please preview & download from browser.",
                "fallback": "browser"
            }), 200

        return jsonify({"error": "Download failed: " + err}), 500

    if not os.path.exists(filepath):
        return jsonify({"error": "File not created"}), 500

    return send_file(filepath, as_attachment=True, download_name="video.mp4")

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
