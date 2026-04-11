# 🚀 Turbo Share - Instant P2P File Sharing

**Turbo Share** is a modern, lightweight, and secure file-sharing web application built with Python (Flask). It allows users to upload files and generate a secure link that automatically expires after 15 minutes. Designed with a focus on speed, privacy, and aesthetic user experience.

---

## 🔗 Live Demo
Experience the app live here: **[Turbo Share Live](https://turbo-share.onrender.com/)**

---

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

---

## ✨ Features

* **⚡ Rapid Upload:** Streamlined process for getting your files onto the cloud instantly.
* **🔒 Strict Privacy:** Files are renamed to unique random IDs on the server to prevent unauthorized access or file-name sniffing.
* **⏳ Auto-Destruction:** Built-in background worker that automatically deletes files and expires links after **15 minutes**.
* **💎 Modern UI:** Premium glassmorphism design with a dark-themed interface for a high-end feel.
* **📎 Smart Copy:** One-click clipboard functionality to share links quickly.
* **📁 Original Name Restore:** Even though files are stored securely with IDs, they are restored to their original filenames upon download.

---

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Server:** Gunicorn (Production ready)
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript (ES6+)
- **Background Tasks:** Python Threading (Cleanup Worker)

---

## 📂 Project Structure

```text
├── app.py              # Main Flask application with cleanup logic
├── requirements.txt    # Project dependencies
├── templates/
│   └── index.html      # Glassmorphism UI
├── uploads/            # Temporary directory for uploaded files
└── README.md           # Documentation
```
---
## 🛡️ Security Note
Turbo Share uses an Ephemeral File System strategy. Files are stored temporarily and cleared periodically. This ensures that no user data persists on the server beyond its intended lifespan, providing a high level of data privacy.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

Developed with ❤️ by Nazmus Sakib Shohan
---
