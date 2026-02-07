# 🎨 Toonify SaaS - AI-Powered Image Stylization Platform

## Project Overview
Toonify is an advanced, production-ready image processing platform that transforms photos into stunning cartoon-style effects using OpenCV and AI. This version is built on a **modern Flask-based architecture** with a premium HTML/JS frontend, offering faster processing, Razorpay integration, and a sophisticated user experience.

## ✨ Key Features

### 1. User Authentication & Security
- Secure registration with email verification
- Google OAuth 2.0 Integration
- bcrypt password hashing
- Session-based security
- SQLite persistence

### 2. Advanced Artistic Styles (9 Total)
- 🎨 **3D Pixar**: Classic 3D cartoon effect
- ✏️ **Lead Sketch**: Detailed pencil sketch
- 🖍️ **Color Pencil**: Vibrant drawing simulation
- 🎭 **Oil Master**: Rich oil painting texture
- 💧 **Watercolor**: Soft artistic washes
- 🎪 **Pop Art**: Bold retro styling
- 📷 **Vintage**: Nostalgic film aesthetics
- 🌸 **Anime**: Japanese manga style
- 💥 **Comic Book**: Action-oriented halftone art

### 3. Premium UI/UX
- Side-by-side comparison stage
- Dynamic before/after slider
- Neural production dashboard
- Ultra-HD export capability
- Responsive desktop & mobile design

### 4. Enterprise Payments
- **Razorpay Integration**: Secure transaction processing
- **Stripe Support**: Global payment ready
- **Demo Mode**: Test all features for free
- Transaction logging and history

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Premium HTML5, CSS3, Vanilla JS
- **Image Processing**: OpenCV, NumPy, Pillow
- **Database**: SQLite3
- **Security**: bcrypt, Google Identity Services
- **Payments**: Razorpay, Stripe

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start (Windows)
1. **Run Setup**:
   ```bash
   setup.bat
   ```
2. **Run Application**:
   ```bash
   run.bat
   ```

### Manual Setup
1. **Activate Virtual Env**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize Database**:
   ```bash
   python scripts/init_db.py
   ```
4. **Run Server**:
   ```bash
   python backend.py
   ```
   *Access at: http://localhost:5000*

## 📁 Project Structure
```
AI-Powered Image Stylization/
├── backend.py              # Main Flask server
├── requirements.txt        # Dependencies
├── .env                    # Configuration
├── templates/              # HTML UIs
│   └── index.html          # Main SaaS Dashboard
├── static/                 # CSS, JS, Assets
├── modules/                # Business logic
│   ├── image_processing.py # AI Stylization engine
│   ├── authentication.py   # Auth & Security
│   ├── payment.py          # Razorpay/Stripe logic
│   └── database.py         # persistent storage
└── scripts/                # Setup & maintenance
```

## 🧪 Testing
Run the comprehensive test suite to ensure stability:
```bash
pytest tests/
```

## 👨‍💻 Developer
**Pruthviraj Tarode**
Version 2.0.0 (February 2026)

---
**Made with ❤️ for digital creators**
