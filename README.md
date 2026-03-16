# <p align="center">Toonify AI</p>

<p align="center"><strong>Professional image stylization platform with live AI art styles, batch processing, AR camera support, secure payments, and a full creator dashboard.</strong></p>

<p align="center">
  <a href="https://toonify.live/"><strong>Live Demo</strong></a>
  |
  <a href="docs/user_guide.md"><strong>User Guide</strong></a>
  |
  <a href="docs/developer_guide.md"><strong>Developer Guide</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-29c55e?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Flask-111827?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Frontend-HTML%20%2F%20CSS%20%2F%20JS-f97316?style=for-the-badge" alt="Frontend">
  <img src="https://img.shields.io/badge/Payments-Razorpay-2563eb?style=for-the-badge" alt="Payments">
  <img src="https://img.shields.io/badge/License-MIT-0f172a?style=for-the-badge" alt="License">
</p>

---

## Product Snapshot

Toonify AI turns ordinary photos into polished AI artwork through a modern creator workflow. The project combines a public landing page, neural editor, payment system, gallery, documentation hub, and creator dashboard in one production-ready Flask application.

---

## Actual Homepage UI

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_pixar_1772354102626.png" alt="Live homepage AI hero artwork" width="58%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_original_1772354038120.png" alt="Live homepage original preview" width="20%">
</p>

<p align="center"><em>The real homepage flow: original preview card plus the main AI-generated artwork panel.</em></p>

---

## Style Preview

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_original_1772354038120.png" alt="Original portrait" width="22%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_pixar_1772354102626.png" alt="Pixar style" width="22%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_anime_1772354129553.png" alt="Anime style" width="22%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/hero_boy_comic_1772354167736.png" alt="Comic style" width="22%">
</p>

<p align="center"><em>One original image transformed across multiple styles that are visible in the live product.</em></p>

---

## UI Gallery

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/cartoon_effect.png" alt="Cartoon effect" width="45%">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/stroke_style.png" alt="Stroke style" width="45%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/pruthvirajtarode/AI-Powered-Image-Stylization-and-Cartoonization-Platform/main/frontend/static/images/gallery_3d_cartoon.png" alt="Gallery preview" width="72%">
</p>

---

## Core Features

| Area | What It Includes |
| :--- | :--- |
| AI generation | 9 art styles, single-image flow, batch processing, creator-friendly output pipeline |
| Product UI | Landing page, neural editor, gallery, docs, billing, profile, and creator dashboard |
| Dashboard | Stylization stats, favorite style, spend tracking, and recent production history |
| Payments | Razorpay integration, secure access flow, payment history, and premium purchase support |
| Extended channels | AR camera support, WhatsApp-related backend modules, and social-content workflows |
| Reliability | Session-aware dashboard behavior and graceful unauthorized handling |

---

## Why This Project Stands Out

- Modern creator-facing UI with a polished landing page and a production-ready feel.
- Real image transformation previews integrated directly into the public product experience.
- Full-stack workflow covering authentication, payments, gallery history, and dashboard analytics.
- Clear separation of frontend, backend, docs, assets, and tests for maintainability.

---

## Tech Stack

| Layer | Stack |
| :--- | :--- |
| Backend | Python, Flask, OpenCV |
| Frontend | HTML5, CSS3, JavaScript |
| Database and auth | PostgreSQL, Bcrypt, session-based authentication |
| Payments | Razorpay |
| Deployment | Render, Docker, Procfile-based startup |

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
  config/
  modules/
  scripts/
  tests/
  utils/
docs/
assets/
data/
```

---

## Getting Started

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

3. Configure environment variables in `backend/` for Google OAuth, Razorpay, database access, and deployment secrets.

4. Start the application.

```bash
python backend/backend.py
```

5. Open the app at `http://localhost:5000`.

---

## Main User Flows

1. Upload a photo from the homepage or editor.
2. Apply a style and preview the transformed output.
3. Download, save, or continue processing additional images.
4. Review previous creations in the gallery.
5. Track usage, favorite style, and spend from the dashboard.

---

## Documentation

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Flowchart](docs/FLOWCHART.md)
- [Project Report](docs/PROJECT_REPORT.md)
- [Issue Resolution Summary](docs/ISSUE_RESOLUTION_SUMMARY.md)
- [New Features Guide](docs/NEW_FEATURES_GUIDE.md)

---

## Recent Improvements

- Dashboard session flow improved to redirect cleanly when login state expires.
- Unauthorized dashboard responses now fail more gracefully.
- README visuals aligned with the actual live product UI.

---

## Contributing

1. Fork the repository.
2. Create a focused feature branch.
3. Keep changes scoped and documented.
4. Open a pull request with a clear summary and screenshots when UI changes are involved.

For bug reports, open a GitHub issue with reproduction steps, expected behavior, and screenshots when relevant.

---

<p align="center"><strong>Built by Pruthviraj Tarode</strong></p>
