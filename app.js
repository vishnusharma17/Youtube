import { exec } from "child_process";
import express from "express";
import fs from "fs";
import path from "path";

const app = express();
const PORT = process.env.PORT || 10000;

// Serve UI
app.get("/", (req, res) => {
  res.sendFile(path.resolve("index.html"));
});

app.get("/api/download", (req, res) => {
  const videoURL = req.query.url;
  if (!videoURL) return res.status(400).send("URL is required");
  const outputPath = "/tmp/video.mp4";

  // ⚡ bot-safe extraction
  const command = `yt-dlp "${videoURL}" -f "bestvideo+bestaudio/best" -o "${outputPath}" --merge-output-format mp4 --no-check-certificate --user-agent "Mozilla/5.0"`;

  exec(command, { maxBuffer: 1024 * 1024 * 200 }, (error, stdout, stderr) => {
    if (error) {
      console.log("STDERR:", stderr);
      return res.status(500).send("Download failed on server");
    }

    if (!fs.existsSync(outputPath)) {
      return res.status(500).send("File not created by yt-dlp");
    }

    res.download(outputPath, "video.mp4", () => {
      try {
        fs.unlinkSync(outputPath);
      } catch {}
    });
  });
});

app.listen(PORT, () => console.log("Server running on", PORT));
