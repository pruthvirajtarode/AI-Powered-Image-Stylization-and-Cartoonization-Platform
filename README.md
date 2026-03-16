# <p align="center">Toonify AI - Professional Image Stylization Platform</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Flask-lightgrey?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Frontend-HTML%20%2F%20CSS%20%2F%20JS-orange?style=for-the-badge" alt="Frontend">
  <img src="https://img.shields.io/badge/License-MIT-black?style=for-the-badge" alt="License">
</p>

<p align="center">
  <strong>Transform your photos into AI artwork with 9 art styles, batch processing, AR camera support, secure payments, and a full creator dashboard.</strong>
</p>

<p align="center">
  <a href="https://toonify.live/"><strong>Live Demo</strong></a>
</p>

---

## Live Product Preview

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_original_1772354038120.png" alt="Original Portrait" width="22%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_pixar_1772354102626.png" alt="3D Pixar Style" width="22%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_anime_1772354129553.png" alt="Anime Style" width="22%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_comic_1772354167736.png" alt="Comic Style" width="22%">
</p>

<p align="center">
  <em>The same style preview sequence used in the live landing-page hero: original upload plus 3D Pixar, Anime, and Comic variants.</em>
</p>

---

## What The Platform Includes

### 1. AI Art Generation
- 9 AI art styles highlighted on the live homepage.
- Fast single-image and batch image processing workflows.
- Portrait, landscape, pet, and creator-friendly outputs.

### 2. Modern Creator UI
- Live landing page with interactive hero preview and style switching.
- Neural editor flow with upload, stylization, and export actions.
- Gallery, docs, billing, dashboard, and profile screens.

### 3. Creator Account System
- Login and profile management.
- Personal dashboard with total stylizations, favorite style, spend, and recent history.
- Session-aware dashboard behavior for expired logins.

### 4. Payments And Delivery
- Razorpay integration for premium purchases and exports.
- Secure access to processed results.
- Download and billing history support.

### 5. Extended Features
- AR camera support.
- WhatsApp and social workflow support in the backend.
- Documentation pages, tutorials, and project guides.

---

## Current UI Screens

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/cartoon_effect.png" alt="Cartoon Effect UI" width="45%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/stroke_style.png" alt="Stroke Style UI" width="45%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/gallery_3d_cartoon.png" alt="Gallery Preview" width="70%">
</p>

<p align="center">
  <em>Current production visuals used by the landing page and gallery experience.</em>
</p>

---

## Recent Updates

- Dashboard handling improved so expired sessions redirect cleanly to login.
- Unauthorized dashboard access now fails gracefully instead of leaving empty stats panels.
- README visuals updated to reflect the current live product UI instead of older placeholder screenshots.

---

## Tech Stack

| Backend | Frontend | Database And Security |
| :--- | :--- | :--- |
| Python | HTML5 | PostgreSQL |
| Flask | CSS3 | Bcrypt |
| OpenCV | JavaScript | Session-based authentication |
| Razorpay integration | Responsive UI | Secure payment tracking |

---

## Project Structure

```text
frontend/
  static/
    css/
    images/
    js/
  templates/
backend/
  modules/
  scripts/
  tests/
docs/
assets/
```

---

## Installation And Setup

1. Clone the repository.

```bash
git clone https://github.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform.git
cd AI-Powered-Image-Stylization-and-Cartoonization-Platform
```

2. Install dependencies.

```powershell
./setup.bat
```

Manual alternative:

```bash
pip install -r backend/requirements.txt
```

3. Configure environment variables in `backend/` for Google OAuth, Razorpay, and deployment secrets.

4. Start the app.

```bash
python backend/backend.py
```

5. Open the app at `http://localhost:5000`.

---

## Main User Flows

- Upload a photo and apply a style from the editor.
- Preview style output and compare creative variations.
- Save or download processed images.
- Review account usage in the dashboard.
- Browse previous outputs in the gallery.
- Track purchases from billing and payment history.

---

## Docs And Guides

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Flowchart](docs/FLOWCHART.md)
- [Project Report](docs/PROJECT_REPORT.md)
- [Issue Resolution Summary](docs/ISSUE_RESOLUTION_SUMMARY.md)

---

## Contributing And Support

1. Fork the repository.
2. Create a feature branch.
3. Make focused changes.
4. Open a pull request with a clear summary.

For bug reports, open a GitHub issue with steps, screenshots, and expected behavior.

---

<p align="center">
  Built by <strong>Pruthviraj Tarode</strong>
</p>
