from flask import Flask, request, jsonify
import os, random, subprocess, dropbox
from moviepy.editor import VideoFileClip

app = Flask(__name__)

DROPBOX_ACCESS_TOKEN = "sl.u.AFzj2LatLguSL5olZiWrBMu8egV_ZUGapiu65rnbXwa_JBP2wxLWzcQiEte9O6z1xTI1zsAUq3HoUFCHjCBDafXvUff05ua6GnwqVZdFrP37lcMsPav1RrdpOGZ_WsbUkJUZaA4p4KbCiHBbw5wYB4UQ7kocw0J3-aQg0v1oq8xIGYnbhJLSGsN4D6-sUz9PnyWcLvbVk1DkkMSU10PLc9f9MyFSK5whHFA91YDp7Fng-uz70gWnyaDpr90g93pnBQSMsLpo5T2LbL1Y0bYDoKhuPD8FrejuiRy9vSHMA0TU7eXojCW9x21vbUdYtGzzyNRqjmU_JLnQwCcPmWv_7udFOCcAUIr2aZM_eAEtbBDhz0eh3C7OieTHygQU3YH56yiGW3TT8lO9cS_A-p5Di7wfLbhe3X_2jIr-atPerPnjjzCOIsKLaS2Rw4bVFFeAHBC-VFuFMl849eVC2XiIagsAzAwoYjEFDnIYVFvFlQkxreIICkEcCNa0iMVr4Gc1GS165xu4k939hayGyXgqrcBrrLwTuNRsaY9aRliPozOFIJ6GjxXVclLkxZl32CgEpJ6DGTuLQzvqcM5fi2d33QrUuZA1AtEotmrRY0FXjMOnQzvQM7E7w7nOGKICAi72hfWABjllmhfwaUhrZHKNqlx3M37CDMrUR7uzNLGOIOcycQu2puW-fZWtlSfnxLVuBnRCFCnQCtTd8S0XNNEtY3Wg8CzVWa_qabuTalUVnroGC1oLKFY0NxdobA7-cvvSPHdXN97Vyp5YP36kcR0DeqPeEj_f0Pja5KLTLWzy2bKKU7fI2brPC3VcXby542_k7xLmHer9pdm1VbDvRFiuDdiSeO_ZDp-eAWqFHG0CNiZDeIDRc0G6cMBGS3Qh_YQ8hLEsg2ksyTDzaPT4X4WudMvC6a3YFlPH6Z8vnYAu6hX4OgnBbjmhsqz0278mZd1QWilAEX1ONbEGiLB5gef5oLHm0oURe7-9n9K8jqQe4AA49Mn-zg5BNsNl1nihL_UaDicDSo8oMju2PgKKc9U4nRowCQP9gaKLQUNla2YNwrXi5v4GurwrKXitcyszm271lu1KSjvnFUin6Dy3CC_JlCIPegDKyct9JWdKaDQp3t6AiHhkikjenKn9ax79mlHJhu1ULhTozGl41yfFvQC5cQCyxXhKcIAOgz3XrTYMp8gVrRQwrSU2iixgjdzQbl9199ea3JCYNhXJxv5oNOckGMyJZ1RflwXdpS5SsU2SKEKcx7szgTydf5L77wraM8NtxSvaWfgcuaayBfccAkC3F01z"

@app.route("/process", methods=["POST"])
def process_video():
    data = request.get_json()
    url = data.get("video_url")
    if not url:
        return jsonify({"error": "No video_url provided"}), 400

    video_id = str(random.randint(1000, 9999))
    filename = f"{video_id}.mp4"
    subprocess.run(["yt-dlp", "-f", "best[height<=1080]", "-o", filename, url])

    clip = VideoFileClip(filename)
    start = 0 if clip.duration <= 60 else random.randint(0, int(clip.duration - 60))
    short_clip = clip.subclip(start, start + 60)

    short_filename = f"clip_{video_id}.mp4"
    short_clip.write_videofile(short_filename, fps=30)

    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    dropbox_path = f"/mrbeast_reels/{short_filename}"
    with open(short_filename, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

    shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    public_url = shared_link.url.replace("?dl=0", "?raw=1")

    os.remove(filename)
    os.remove(short_filename)

    return jsonify({"video_url": public_url})

@app.route("/")
def home():
    return "Video Clipper API is live"

if __name__ == "__main__":
    app.run()
