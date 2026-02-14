# Toonify AI - Professional Image Stylization Platform 🎨🤖

Welcome to **Toonify AI**, a premium, state-of-the-art platform that transforms your photos into stunning artistic masterpieces using advanced neural calculations and high-performance OpenCV algorithms.

## 🚀 Key Features

### 1. Neural Stylization Engine (Milestone 1)
- **Real-time Processing**: High-speed image transformation for Cartoon, Pencil Sketch, Anime, Oil Painting, and more.
- **Advanced Showcase**: Dynamic A/B comparison slider and side-by-side view to witness the artistic transformation.
- **Neural Statistics (Task 13)**: In-depth analysis of Brightness, Contrast, and Color Distribution for every generation.

### 2. Premium Monetization (Milestone 2)
- **Monetization Engine**: Integrated **Razorpay** for seamless HD exports and Pro subscriptions.
- **Multi-Format Exports (Task 14)**: Export your creations in high-quality **JPG**, lossless **PNG**, or professional **PDF**.
- **Secure Watermarking**: Subtle watermarks for free previews that vanish instantly upon payment verification.
- **Elite Downloads (Task 17)**: Signed, temporary download links ensuring highest security for your neural exports.

### 3. Personal Creative Vault (Task 18)
- **Neural History**: A comprehensive, paginated gallery of all your past creations.
- **Smart Filtering**: Sort and filter by style, date, or processing speed.
- **Bulk Recovery**: One-click "Download All" feature that packages your entire history into a secure ZIP archive.
- **Privacy Controls**: "Neural Burn" (Danger Zone) for permanent data wiping and auto-delete settings (7/30/90 days).

## 🛠️ Tech Stack
- **Backend**: Python 3.9+, Flask, OpenCV (CV2), NumPy, itsdangerous
- **Frontend**: Vanilla JavaScript (ES6+), Modern HTML5, Glassmorphic CSS3
- **Database**: PostgreSQL (Production ready) / SQLite (Local dev)
- **Security**: Bcrypt hashing, URL-signed tokens, Session-based auth
- **Payments**: Razorpay API (Stripe compatible layer)

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/toonify-ai.git
   cd toonify-ai
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file (or update `config/settings.py`) with:
   - `GOOGLE_CLIENT_ID`
   - `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET`
   - `DATABASE_URL`

4. **Run the Engine**:
   ```bash
   python backend/backend.py
   ```
   *Dashboard will be live at `http://localhost:5000`*

## 🎨 Dashboard Tour
- **Home**: Upload directly via Drag-and-Drop or Camera Capture.
- **Dashboard**: View your Account Statistics, Favorite Styles, and Lifetime Spend.
- **Vault**: Search through your historical art pieces and manage your exports.
- **Profile**: Multi-layer security settings including Password Rotations and Account Privacy.

---
*Created with ❤️ by the Antigravity AI Coding Assistant.*
