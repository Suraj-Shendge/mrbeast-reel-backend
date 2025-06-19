from flask import Flask, request, jsonify
import os, random, subprocess, dropbox, whisper
from moviepy.editor import VideoFileClip

app = Flask(__name__)
model = whisper.load_model("base")
DROPBOX_ACCESS_TOKEN = "your_token_here"

@app.route("/process", methods=["POST"])
def process_video():
    data = request.get_json()
    url = data.get("video_url")
    video_id = str(random.randint(1000, 9999))
    filename = f"{video_id}.mp4"

    subprocess.run(["yt-dlp", "-f", "best[height<=1080]", "-o", filename, url])
    clip = VideoFileClip(filename)
    start = 0 if clip.duration <= 60 else random.randint(0, int(clip.duration - 60))
    short_clip = clip.subclip(start, start + 60)
    short_filename = f"clip_{video_id}.mp4"
    short_clip.write_videofile(short_filename, fps=30)

    result = model.transcribe(short_filename)
    subtitles = result["text"]

    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    dropbox_path = f"/mrbeast_reels/{short_filename}"
    with open(short_filename, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    public_url = shared_link.url.replace("?dl=0", "?raw=1")

    os.remove(filename)
    os.remove(short_filename)

    return jsonify({"video_url": public_url, "subtitles": subtitles[:200] + "..."})

@app.route("/")
def home():
    return "Backend is live"

if __name__ == "__main__":
    app.run()
