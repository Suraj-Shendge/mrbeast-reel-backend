from flask import Flask, request, jsonify
import os
import random
from moviepy.editor import VideoFileClip
from yt_dlp import YoutubeDL
import dropbox

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    try:
        url = request.json.get("video_url")
        if not url:
            return jsonify({"error": "Missing video_url"}), 400

        filename = f"{random.randint(1000,9999)}.mp4"

        # Download video using yt_dlp
        ydl_opts = {
            'outtmpl': filename,
            'quiet': True,
            'format': 'mp4/bestvideo',
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Confirm file exists
        if not os.path.exists(filename):
            return jsonify({"error": f"Download failed, file {filename} not found"}), 500

        # Clip the video to 60 seconds
        clip = VideoFileClip(filename).subclip(0, 60)
        clipped_filename = "clip_" + filename
        clip.write_videofile(clipped_filename, codec='libx264', audio_codec='aac')

        # Upload to Dropbox
        DROPBOX_TOKEN = os.getenv("sl.u.AFyc1RUpPKhyon5bXl1JplQj0dSNlbAch2Mv-jPHzb1lGdfHAh3DNrkOA0EBs_lmTzlMWykgkzYEs0ZFTYQg8YKvn99jfP1W5eKnNfUicB0uQvK1U9qU45QstYpZ_AT18ysonunXMh29dI7mVSe1rPDhAfM7eC25tRd7H03KLL3DQfJfyhTN9SXKQ1aQ5UgbXjuu6PEOfXwPvPkjpXY19OiQb2PcTPFelHk2AL5UsAKRRB3pbSp_TMjfqi4bnQTmvFUoTfeElmzARQnudD7QskyDYOqYCJ1kpEPIbMpUA7XFsGcQXfI-PCEqC9quK687aoripT_Iko1VJVQLXb8I_-S-Fw4SYmuIgqgQVM_grJt--9CtD7KcKl-eqpUei8KUVHcZnJ-y12UYuiGCwLg8Ma22SYzUVhzfJnFJVQagGkXK-M09wBN08xsUieAPHRQtHWVCZcJopiBBPIURGDh5qHyiGc7CGhOw3K_w0XutdD5nNfmEyW9V4FPAFOWuIOnztlg71u7NQKlBAkOVsnjdXRVE7UShTKK1343IZWlgkxNBXcxKBnsyukUhrJMIABoT4jBxYfN7iBBufb4bRzu0e3WHUX9QeIX6uZI7_OWLAaShaIMkn2ZO4cmHmm2PwDwDSLEzENTbTNxsl729yBacdvqhZ-WjjopKwnUI8YY5xm_PUfxvT6X0n9hJOsX9U7Vo475UjrlhIeKfKS6YOnD929UUTasqyYN0f8NUgDUH1Go5J1UZXo0EIalSGJioJB7hm-cLSnxgVDec8SR2gsAODvyJoSd2lVf7wXSZPm-Lbl1sueIvsISy0vJkQ0X-mBNNlSwgmtpzGK0l0Z5vsRRLW_sYEf-6QCLfL5U3V4OirvBZk4W1mDkNnxmjvfca_RCqx1QzE1JybYqxJ3NW-5B0wRK0uRyVoHxUk5ZGNRpj8ifj7j-_U-EkAzwb0HiZkBd-ZfCbk0eEky0hf7PNJbj6qkyQm7VCZIBqOf0WWENeQT4KWU0ITHKXXJFSckWVC439V00WMiVOK7rhOcQrjvWwLxSvb2gnE3N3RGodeZkI2zQZ0siG4fO1dBqm_X96xnSXkoc6eXjBp05kkYOpOdwD-wCHlIkFyGjl9EiquzPIMQiyJLV3mjlKCCDppxe6B-oItO1QNGi5A1DST3AtVgN23cEfZtx7WCWyMsMZQX3Y06ign4ONLZSmKs6AvQF44zuzXDnr-UbsuWMhhO_nLkS_1ipgGNtojAGd_3k2k1A4bWW05xdGvfLru4vTX9dEHTpG6nnoeB4SQGvs75mWPkpFcS-b")
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)

        with open(clipped_filename, "rb") as f:
            dbx.files_upload(f.read(), f"/{clipped_filename}", mode=dropbox.files.WriteMode.overwrite)

        shared_link = dbx.sharing_create_shared_link_with_settings(f"/{clipped_filename}").url
        final_url = shared_link.replace("?dl=0", "?raw=1")

        # Cleanup
        os.remove(filename)
        os.remove(clipped_filename)

        return jsonify({"video_url": final_url})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
