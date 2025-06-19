from flask import Flask, request, jsonify
import os, subprocess, random, dropbox
from moviepy.editor import VideoFileClip

app = Flask(__name__)

DROPBOX_ACCESS_TOKEN = "sl.u.AFyc1RUpPKhyon5bXl1JplQj0dSNlbAch2Mv-jPHzb1lGdfHAh3DNrkOA0EBs_lmTzlMWykgkzYEs0ZFTYQg8YKvn99jfP1W5eKnNfUicB0uQvK1U9qU45QstYpZ_AT18ysonunXMh29dI7mVSe1rPDhAfM7eC25tRd7H03KLL3DQfJfyhTN9SXKQ1aQ5UgbXjuu6PEOfXwPvPkjpXY19OiQb2PcTPFelHk2AL5UsAKRRB3pbSp_TMjfqi4bnQTmvFUoTfeElmzARQnudD7QskyDYOqYCJ1kpEPIbMpUA7XFsGcQXfI-PCEqC9quK687aoripT_Iko1VJVQLXb8I_-S-Fw4SYmuIgqgQVM_grJt--9CtD7KcKl-eqpUei8KUVHcZnJ-y12UYuiGCwLg8Ma22SYzUVhzfJnFJVQagGkXK-M09wBN08xsUieAPHRQtHWVCZcJopiBBPIURGDh5qHyiGc7CGhOw3K_w0XutdD5nNfmEyW9V4FPAFOWuIOnztlg71u7NQKlBAkOVsnjdXRVE7UShTKK1343IZWlgkxNBXcxKBnsyukUhrJMIABoT4jBxYfN7iBBufb4bRzu0e3WHUX9QeIX6uZI7_OWLAaShaIMkn2ZO4cmHmm2PwDwDSLEzENTbTNxsl729yBacdvqhZ-WjjopKwnUI8YY5xm_PUfxvT6X0n9hJOsX9U7Vo475UjrlhIeKfKS6YOnD929UUTasqyYN0f8NUgDUH1Go5J1UZXo0EIalSGJioJB7hm-cLSnxgVDec8SR2gsAODvyJoSd2lVf7wXSZPm-Lbl1sueIvsISy0vJkQ0X-mBNNlSwgmtpzGK0l0Z5vsRRLW_sYEf-6QCLfL5U3V4OirvBZk4W1mDkNnxmjvfca_RCqx1QzE1JybYqxJ3NW-5B0wRK0uRyVoHxUk5ZGNRpj8ifj7j-_U-EkAzwb0HiZkBd-ZfCbk0eEky0hf7PNJbj6qkyQm7VCZIBqOf0WWENeQT4KWU0ITHKXXJFSckWVC439V00WMiVOK7rhOcQrjvWwLxSvb2gnE3N3RGodeZkI2zQZ0siG4fO1dBqm_X96xnSXkoc6eXjBp05kkYOpOdwD-wCHlIkFyGjl9EiquzPIMQiyJLV3mjlKCCDppxe6B-oItO1QNGi5A1DST3AtVgN23cEfZtx7WCWyMsMZQX3Y06ign4ONLZSmKs6AvQF44zuzXDnr-UbsuWMhhO_nLkS_1ipgGNtojAGd_3k2k1A4bWW05xdGvfLru4vTX9dEHTpG6nnoeB4SQGvs75mWPkpFcS-b"

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    url = data.get("video_url")
    if not url:
        return jsonify({"error": "Missing video_url"}), 400

    # Download
    video_id = str(random.randint(1000, 9999))
    filename = f"{video_id}.mp4"
    subprocess.run(["yt-dlp", "-f", "best[height<=1080]", "-o", filename, url])

    # Clip
    clip = VideoFileClip(filename)
    start = 0 if clip.duration <= 60 else random.randint(0, int(clip.duration - 60))
    subclip = clip.subclip(start, start + 60)
    short_filename = f"clip_{video_id}.mp4"
    subclip.write_videofile(short_filename, fps=30)

    # Upload to Dropbox
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    path = f"/clips/{short_filename}"
    with open(short_filename, "rb") as f:
        dbx.files_upload(f.read(), path, mode=dropbox.files.WriteMode.overwrite)
    shared = dbx.sharing_create_shared_link_with_settings(path)
    link = shared.url.replace("?dl=0", "?raw=1")

    # Cleanup
    os.remove(filename)
    os.remove(short_filename)

    return jsonify({"video_url": link})

@app.route("/")
def home():
    return "API is live"
