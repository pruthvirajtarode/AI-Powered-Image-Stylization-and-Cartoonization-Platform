# 📊 Toonify AI - Architecture Diagrams Guide

This directory contains comprehensive architecture diagrams for the Toonify AI project in multiple formats.

## 📁 Files Overview

### Diagram Files (Mermaid Format)
- **system_workflow.md** - Complete image processing workflow
- **usecase_diagram.md** - User roles and system interactions
- **sequence_diagram.md** - Component interaction sequence
- **class_diagram.md** - System architecture and classes

### Conversion Scripts
- **generate_diagrams.py** - Python script for PNG generation
- **convert_diagrams.bat** - Windows batch script
- **convert_diagrams.sh** - Linux/Mac bash script
- **diagram_viewer.html** - Interactive web viewer

## 🎯 Quick Start

### Option 1: View Online (No Installation Required) ✨

1. **Visit Mermaid Live Editor**: https://mermaid.live/
2. **Copy & Paste** the Mermaid code from any `.md` file in this directory
3. **Download as PNG** directly from the interface

### Option 2: Use Interactive HTML Viewer 🌐

Run from the project root:
```bash
python generate_diagrams.py
```

Then open `diagram_viewer.html` in your browser to view all diagrams interactively.

### Option 3: Generate PNG Files Locally 🖼️

#### On Windows:
```batch
npm install -g mermaid-cli
convert_diagrams.bat
```

#### On macOS/Linux:
```bash
npm install -g mermaid-cli
bash convert_diagrams.sh
```

#### Using Docker (Any OS):
```bash
docker run --rm -v $(pwd):/data minlag/mermaid-cli \
  -i /data/docs/diagrams/system_workflow.md \
  -o /data/docs/diagrams/output/01_System_Workflow.png
```

## 📊 Diagram Descriptions

### 1. System Workflow Diagram
**File**: `system_workflow.md`

Shows the complete journey of an image through Toonify AI:
- User authentication (OAuth 2.0)
- Image validation
- Style processing (Pixar, Anime, Comic, etc.)
- Quality selection (Premium vs Free)
- Export options (WhatsApp, Instagram, Download)
- Analytics tracking

### 2. Use Case Diagram
**File**: `usecase_diagram.md`

Illustrates three types of users and their interactions:

**Free Users** can:
- Upload images
- Select styles
- Process images
- Download standard quality
- Manage accounts

**Premium Users** can:
- All free user features
- Download 4K quality
- Share on social media (WhatsApp, Instagram)
- View analytics dashboard
- Manage payment methods

**Admin Users** can:
- System administration
- View all analytics
- Manage payments
- System configuration

### 3. Sequence Diagram
**File**: `sequence_diagram.md`

Details the step-by-step interactions:
1. **Upload Phase**: User uploads → Frontend → Backend validation
2. **Authentication**: Session verification with database
3. **Processing Phase**: Image selection → OpenCV processing → Neural style application
4. **Database**: Saving processing records
5. **Download Phase**: Premium verification → Quality rendering → Export
6. **Social Sharing**: WhatsApp integration and compression

### 4. Class Diagram
**File**: `class_diagram.md`

Shows core architecture components:

**Main Classes**:
- `Flask_App`: Main application server
- `Authentication`: User login and OAuth
- `ImageProcessor`: Image transformation engine
- `Database`: Data persistence layer
- `User`: User entity
- `ProcessingRecord`: Image processing history
- `PaymentProcessor`: Razorpay integration
- `WhatsAppProcessor`: WhatsApp API integration
- `Config`: Configuration management

**Key Relationships**:
- Flask orchestrates all modules
- Database manages two main entities: User and ProcessingRecord
- Each processing module links through Flask_App
- External integrations (Payment, WhatsApp) connect via Flask

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 12+ (for mermaid-cli)
- npm or yarn

### Installation Steps

1. **Install mermaid-cli globally**:
   ```bash
   npm install -g mermaid-cli
   ```

2. **From project root, run conversion**:
   ```bash
   # Windows
   convert_diagrams.bat
   
   # macOS/Linux
   bash convert_diagrams.sh
   ```

3. **Output**:
   - PNGs saved to: `docs/diagrams/output/`
   - Resolution: 1920x1080 (Full HD, clear for presentations)

## 📱 Using Diagrams

### For Presentations
- Use PNGs with 1920x1080 resolution for projection
- All diagrams are color-coded for clarity
- Recommended: Use diagrams in PowerPoint, Google Slides, or Keynote

### For Documentation
- Embed PNGs in README, wikis, or documentation
- Reference Mermaid code in markdown for CI/CD rendering

### For Development
- Keep `.md` files in version control
- Update diagrams when architecture changes
- Regenerate PNGs for releases

## 🎨 Diagram Features

All diagrams include:
- ✅ Clear labeled components
- ✅ Color-coded sections
- ✅ Emoji indicators for quick recognition
- ✅ System interactions and data flow
- ✅ Role-based access patterns
- ✅ Integration points

## 📝 Notes

- **Mermaid Version**: Compatible with Mermaid v9+
- **Format**: SVG output (scalable, high-quality)
- **Browser Support**: Chrome, Firefox, Safari, Edge (all modern versions)
- **Accessibility**: All diagrams include text labels and descriptions

## ❓ Troubleshooting

### "mermaid-cli not found"
```bash
npm install -g mermaid-cli
which mmdc  # Verify installation
```

### "PNG output is blurry"
Ensure you're using v10+ of mermaid-cli:
```bash
npm list -g mermaid-cli
npm install -g mermaid-cli@latest  # Update if needed
```

### Docker alternative
If npm installation fails:
```bash
# Install Docker first, then:
docker run --rm -v $(pwd):/data minlag/mermaid-cli \
  -i /data/docs/diagrams/ \
  -o /data/docs/diagrams/output/ \
  -w 1920 -H 1080
```

## 📞 Support

For diagram-related questions:
1. Check the inline descriptions in each `.md` file
2. Review Mermaid documentation: https://mermaid.js.org/
3. Test online at: https://mermaid.live/

---

**Last Updated**: March 2026
**Format**: Mermaid 9+
**Status**: Production Ready
