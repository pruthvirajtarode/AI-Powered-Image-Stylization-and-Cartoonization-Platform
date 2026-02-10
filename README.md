# 🎨 Toonify SaaS - AI-Powered Image Stylization

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=render)](https://toonify-ai-saas.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-orange?style=for-the-badge&logo=opencv)](https://opencv.org/)

**Toonify** is an advanced, production-ready image processing platform that transforms photos into stunning cartoon-style effects using OpenCV and AI. Built with a modern Flask architecture and a premium glassmorphic frontend.

---

## 🚀 Live Platform
Experience the magic here: **[https://toonify-ai-saas.onrender.com/](https://toonify-ai-saas.onrender.com/)**

---

## ✨ Key Features

### 🔐 User Authentication & Security
- **Secure Access**: Registration with email verification & Google OAuth 2.0.
- **Data Protection**: bcrypt password hashing and session-based security.
- **Persistence**: Robust SQLite integration for user profiles and history.

### 🎭 9 Artistic Styles
| Style | Description |
| :--- | :--- |
| 🎨 **3D Pixar** | Classic 3D cartoon movie effects |
| ✏️ **Lead Sketch** | Detailed high-contrast pencil sketches |
| 🖍️ **Color Pencil** | Vibrant drawing and shading simulation |
| 🎭 **Oil Master** | Rich, textured oil painting aesthetics |
| 💧 **Watercolor** | Soft, bleeding artistic washes |
| 🎪 **Pop Art** | Bold retro styling with halftone effects |
| 📷 **Vintage** | Nostalgic film aesthetics and grain |
| 🌸 **Anime** | Sharp, vibrant Japanese manga style |
| 💥 **Comic Book** | Action-oriented bold strokes |

### 💎 Premium UI/UX
- **Comparison Stage**: Side-by-side "Before & After" interactive view.
- **Neural Dashboard**: Sophisticated user dashboard for tracking history.
- **Ultra-HD Export**: High-resolution processing for pro-quality results.
- **Responsive Design**: Flawless experience across Desktop, Tablet, and Mobile.

### 💳 Enterprise Payments
- **Multi-Gateway**: Seamless Razorpay & Stripe integration.
- **Demo Mode**: Test drive all AI models for free.
- **History**: Detailed transaction logging and exportable history.

---

## 🛠️ Technology Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=Stripe&logoColor=white)
![Razorpay](https://img.shields.io/badge/Razorpay-02042B?style=for-the-badge&logo=razorpay&logoColor=3399FF)

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### 🏁 Quick Start (Windows)
```powershell
# Run automatic setup
.\setup.bat

# Launch the platform
.\run.bat
```

### 🛠️ Manual Installation
1. **Prepare Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database Initialization**:
   ```bash
   python scripts/init_db.py
   ```
4. **Boot Server**:
   ```bash
   python backend.py
   ```
   *Platform will be live at: http://localhost:5000*

---

## 📁 Project Structure
```text
AI-Powered Image Stylization/
├── backend.py              # Main Flask server & API
├── modules/                # Core Business Logic
│   ├── image_processing.py # AI Stylization engine (OpenCV)
│   ├── authentication.py   # Auth, OAuth & JWT
│   ├── payment.py          # Unified Payment Gateway
│   └── database.py         # ORM & Storage
├── static/                 # Frontend Assets (Glassmorphic CSS, JS)
├── templates/              # Jinja2 HTML Templates
├── scripts/                # Utility & Maintenance
└── tests/                  # Pytest Comprehensive Suite
```

---

## 🧪 Stability Testing
Maintain code quality with our automated test suite:
```bash
pytest tests/
```

---

## 👨‍💻 Developer
**Pruthviraj Tarode**  
*Version 2.0.0 (February 2026)*

---
<p align="center">
  Made with ❤️ for digital creators
</p>
