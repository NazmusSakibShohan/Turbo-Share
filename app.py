import os
import random
import string
import time
import threading
import io
import base64
import qrcode
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

# --- Config ---
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB Limit
LINK_EXPIRY = 15 * 60  # 15 minutes in seconds

# Mapping: { random_id: {"path":..., "time":..., "original_name":...} }
file_links = {}

def generate_random_string(length=6):
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

        random_id = generate_random_string()
        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1]
        safe_filename = f"{random_id}{extension}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)

        file.save(filepath)

        file_links[random_id] = {
            "path": filepath,
            "time": time.time(),
            "original_name": original_filename
        }

        share_link = request.host_url + random_id

        # --- QR Code Generation ---
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(share_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return render_template("index.html", link=share_link, qr_code=qr_base64, error=None)

    return render_template("index.html", link=None, error=None)

@app.route("/<random_id>")
def download(random_id):
    """Serve the file if the link is valid and strictly within the expiration window"""
    file_info = file_links.get(random_id)
    
    if not file_info:
        return "Invalid or expired link", 404

    # --- Strict Expiration Check ---
    now = time.time()
    if now - file_info["time"] > LINK_EXPIRY:
        # Delete file and remove from dictionary if time limit is exceeded
        try:
            if os.path.exists(file_info["path"]):
                os.remove(file_info["path"])
            del file_links[random_id]
        except Exception as e:
            print(f"Cleanup error: {e}")
        return "This link has expired (15 minutes limit exceeded).", 404

    return send_file(
        file_info["path"], 
        as_attachment=True, 
        download_name=file_info["original_name"]
    )

# --- Background Cleanup Logic ---
def cleanup_expired_files():
    """Periodically removes files from the server after they expire"""
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
            if key in file_links:
                del file_links[key]
        time.sleep(60)

# Start background cleanup thread
threading.Thread(target=cleanup_expired_files, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
