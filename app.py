import os
import random
import string
import time
import threading
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

# --- Config ---
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB Limit
LINK_EXPIRY = 15 * 60  # 15 minutes in seconds

# Mapping: { random_id: {"path":..., "time":..., "original_name":...} }
file_links = {}

def generate_random_string(length=12):
    """Generate a unique ID for file links and filenames"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.errorhandler(413)
def file_too_large(e):
    return render_template("index.html", link=None, error="File is too large. Max limit is 25 MB."), 413

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template("index.html", link=None, error="No file selected")

        file = request.files['file']
        if file.filename == "":
            return render_template("index.html", link=None, error="No file selected")

        # 1. Generate unique ID
        random_id = generate_random_string()
        
        # 2. Extract extension and create a safe filename for the server
        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1]
        safe_filename = f"{random_id}{extension}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)

        # 3. Save file to the server
        file.save(filepath)

        # 4. Store metadata including the original filename
        file_links[random_id] = {
            "path": filepath,
            "time": time.time(),
            "original_name": original_filename
        }

        share_link = request.host_url + random_id
        return render_template("index.html", link=share_link, error=None)

    return render_template("index.html", link=None, error=None)

@app.route("/<random_id>")
def download(random_id):
    """Serve the file with its original name if the link is valid"""
    file_info = file_links.get(random_id)
    
    if not file_info:
        return "Invalid or expired link", 404

    # 5. Return the file using its original name for the downloader
    return send_file(
        file_info["path"], 
        as_attachment=True, 
        download_name=file_info["original_name"]
    )

# --- Background Cleanup Logic ---
def cleanup_expired_files():
    """Periodically removes files older than LINK_EXPIRY"""
    while True:
        now = time.time()
        expired_keys = []
        
        for key, info in list(file_links.items()):
            if now - info["time"] > LINK_EXPIRY:
                try:
                    if os.path.exists(info["path"]):
                        os.remove(info["path"])
                except Exception as e:
                    print(f"Error deleting file: {e}")
                expired_keys.append(key)

        for key in expired_keys:
            del file_links[key]

        time.sleep(60)  # Check every minute

# Start the background thread
threading.Thread(target=cleanup_expired_files, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)