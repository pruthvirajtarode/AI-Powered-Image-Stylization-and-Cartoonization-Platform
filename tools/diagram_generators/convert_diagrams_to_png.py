#!/usr/bin/env python3
"""
Convert Mermaid diagrams to PNG using weasyprint or pillow
"""

import subprocess
import sys
import os
from pathlib import Path

def check_and_install_dependencies():
    """Check for required packages and install if needed"""
    packages = {
        'weasyprint': 'WeasyPrint for HTML to PNG conversion',
        'cairosvg': 'CairoSVG for SVG rendering'
    }
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package}: Already installed")
        except ImportError:
            print(f"📦 Installing {description}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def convert_html_to_png():
    """Convert HTML file to PNG using WeasyPrint"""
    try:
        from weasyprint import HTML, CSS
        
        html_file = Path('mermaid_diagrams_export.html')
        output_dir = Path('docs/diagrams/output')
        
        if not html_file.exists():
            print(f"❌ Error: {html_file} not found!")
            return False
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📊 Converting HTML to PNG using WeasyPrint...")
        print(f"   Input: {html_file}")
        print(f"   Output: {output_dir}/")
        
        # For WeasyPrint, we'll convert the whole HTML to PNG
        # This may require Chrome/Firefox backend
        try:
            html = HTML(str(html_file))
            png_path = output_dir / 'diagrams_full.png'
            html.write_png(str(png_path))
            print(f"✅ Created: {png_path}")
            return True
        except Exception as e:
            print(f"⚠️  WeasyPrint method failed: {e}")
            print("   Trying alternative method...")
            return False
            
    except ImportError:
        print("❌ WeasyPrint not available. Trying alternative methods...")
        return False

def convert_with_chrome():
    """Use Chrome/Chromium to convert HTML to PNG"""
    try:
        import json
        from pathlib import Path
        
        html_file = Path('mermaid_diagrams_export.html').absolute()
        output_dir = Path('docs/diagrams/output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Chrome command to take screenshot
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Chromium\Application\chrome.exe",
        ]
        
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if not chrome_path:
            print("⚠️  Chrome not found. Trying Chromium...")
            # Try chromium-browser or other names
            chrome_path = "chrome"  # Will use PATH
        
        print(f"\n📊 Using Chrome to convert HTML to PNG...")
        print(f"   Input: {html_file}")
        print(f"   Output: {output_dir}/")
        
        # Use Chrome headless to take screenshots
        output_png = output_dir / 'diagrams_full.png'
        
        cmd = [
            chrome_path,
            '--headless=new',
            '--disable-gpu',
            '--screenshot',
            f'--window-size=1920,2400',
            f'--screenshot={output_png}',
            f'file:///{html_file}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if output_png.exists():
            print(f"✅ Created: {output_png}")
            print(f"   Size: {output_png.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print(f"⚠️  Chrome method failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Chrome method error: {e}")
        return False

def create_individual_png_guide():
    """Create a guide for manual PNG export"""
    guide = """# 📊 Manual PNG Export Guide

Since automated conversion encountered issues, here are your options:

## Option 1: Browser-Based Export (5 minutes)
1. **Open** `mermaid_diagrams_export.html` in your browser
2. For each diagram:
   - Right-click the diagram
   - Select "Save image as..."
   - Choose PNG format
   - Save to `docs/diagrams/output/` with names:
     * 01_System_Workflow.png
     * 02_UseCase_Diagram.png
     * 03_Sequence_Diagram.png
     * 04_Class_Diagram.png

## Option 2: Online Export (2 minutes)
1. Visit: https://mermaid.live/
2. For each `.mmd` file in `docs/diagrams/`:
   - Open the file in a text editor
   - Copy all the code
   - Paste into Mermaid Live
   - Click "Download" > PNG
   - Save to `docs/diagrams/output/`

## Option 3: Using Print-to-PDF then Convert
1. Open `mermaid_diagrams_export.html`
2. Press Ctrl+P (or Cmd+P)
3. Save as PDF
4. Use an online PDF-to-PNG converter
5. Save to `docs/diagrams/output/`

## Option 4: Command Line (if you have Chrome installed)
```bash
# On Windows:
"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless --screenshot --window-size=1920,2400 file:///C:/path/to/mermaid_diagrams_export.html

# The screenshot will be saved as: screenshot.png
```

## Option 5: Docker (Most Reliable)
```bash
docker run --rm -v $(pwd):/workspace -w /workspace \\
  minlag/mermaid-cli \\
  -i docs/diagrams/system_workflow.mmd \\
  -o docs/diagrams/output/01_System_Workflow.png
```

---

**Recommended**: Use **Option 1 (Browser-Based)** - it's the easiest and most reliable!

"""
    
    guide_path = Path('PNG_EXPORT_GUIDE.md')
    with open(guide_path, 'w') as f:
        f.write(guide)
    
    print(f"✅ Created guide: {guide_path}")
    print("\n" + "="*60)
    print("📖 Check: PNG_EXPORT_GUIDE.md for manual export options")
    print("="*60)

def main():
    print("="*60)
    print("🎨 Toonify AI - PNG Conversion Tool")
    print("="*60)
    
    # Try automated methods
    print("\n🔍 Attempting automated conversion...\n")
    
    # Try Chrome first (faster)
    if convert_with_chrome():
        print("\n✅ PNG conversion completed!")
        return
    
    # Try WeasyPrint
    print("\n📦 Checking Python dependencies...")
    check_and_install_dependencies()
    
    if convert_html_to_png():
        print("\n✅ PNG conversion completed!")
        return
    
    # Fallback to manual guide
    print("\n⚠️  Automated conversion not available")
    print("📋 Creating manual export guide instead...\n")
    create_individual_png_guide()

if __name__ == '__main__':
    main()
