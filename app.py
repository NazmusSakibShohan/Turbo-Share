import os
import random
import string
import time
import threading
import io
import base64
import qrcode
import zipfile
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

# --- Config ---
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  
LINK_EXPIRY = 15 * 60  


file_links = {}

def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.errorhandler(413)
def file_too_large(e):
    return render_template("index.html", link=None, error="Files are too large! Max limit is 50 MB."), 413

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        files = request.files.getlist('file') 

        if not files or all(f.filename == "" for f in files):
            return render_template("index.html", link=None, error="No files selected.")

        total_size = 0
        for f in files:
            f.seek(0, os.SEEK_END)
            total_size += f.tell()
            f.seek(0)
        
        if total_size > app.config['MAX_CONTENT_LENGTH']:
            return render_template("index.html", link=None, error="Total size exceeds 50 MB."), 413

        random_id = generate_random_string()
        
        if len(files) > 1:
            zip_filename = f"TurboShare_{random_id}.zip"
            filepath = os.path.join(UPLOAD_FOLDER, zip_filename)
            original_name = zip_filename
            
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files:
                    if file.filename != "":
                        zipf.writestr(file.filename, file.read())
        else:
            file = files[0]
            original_name = file.filename
            extension = os.path.splitext(original_name)[1]
            safe_filename = f"{random_id}{extension}"
            filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
            file.save(filepath)

        file_links[random_id] = {
            "path": filepath,
            "time": time.time(),
            "original_name": original_name
        }

        share_link = request.host_url + random_id

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
    file_info = file_links.get(random_id)
    if not file_info:
        return "Invalid or expired link", 404

    if time.time() - file_info["time"] > LINK_EXPIRY:
        cleanup_file(random_id)
        return "This link has expired.", 404

    return send_file(
        file_info["path"], 
        as_attachment=True, 
        download_name=file_info["original_name"]
    )

def cleanup_file(rid):
    if rid in file_links:
        try:
            if os.path.exists(file_links[rid]["path"]):
                os.remove(file_links[rid]["path"])
            del file_links[rid]
        except: pass

def background_cleanup():
    while True:
        now = time.time()
        expired_keys = [k for k, v in file_links.items() if now - v["time"] > LINK_EXPIRY]
        for key in expired_keys:
            cleanup_file(key)
        time.sleep(60)

threading.Thread(target=background_cleanup, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
