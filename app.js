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

// Downloader API
app.get("/api/download", (req, res) => {
  const videoURL = req.query.url;
  if (!videoURL) return res.status(400).send("URL is required");

  const outputPath = "/tmp/video.mp4"; // temp folder is best

  const command = `yt-dlp --cookies-from-browser chrome --js-runtimes "deno" "${videoURL}" -o "${outputPath}" --merge-output-format mp4 --no-check-certificate`;

  exec(command, { maxBuffer: 1024 * 1024 * 200 }, (error) => {
    if (error) {
      console.log("YT-DLP ERROR:", error);
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
