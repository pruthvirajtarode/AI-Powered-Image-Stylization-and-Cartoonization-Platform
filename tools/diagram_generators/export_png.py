#!/usr/bin/env python3
"""
Simple PNG export by opening HTML in browser and capturing screenshots
"""

import os
import webbrowser
from pathlib import Path

def main():
    print("="*70)
    print("🎨 Toonify AI - PNG Export Assistant")
    print("="*70)
    
    # Ensure output directory exists
    output_dir = Path('docs/diagrams/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✅ Output directory ready: {output_dir.absolute()}")
    
    html_file = Path('mermaid_diagrams_export.html').absolute()
    
    if not html_file.exists():
        print(f"\n❌ Error: {html_file} not found!")
        return
    
    print("\n" + "="*70)
    print("📊 QUICK PNG EXPORT (30 seconds)")
    print("="*70)
    
    print("""
✨ STEP 1: Browser will open automatically in 3 seconds...
   (If not, manually open: mermaid_diagrams_export.html)

✨ STEP 2: For each diagram (4 total), do this:
   
   1. Right-click on the diagram
   2. Select: "Save image as..."
   3. Name it as shown below
   4. Save to: docs/diagrams/output/
   
   Diagram Names:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📊 01_System_Workflow.png
   🎭 02_UseCase_Diagram.png
   🔄 03_Sequence_Diagram.png
   🏗️  04_Class_Diagram.png
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ STEP 3: Done! All 4 PNG files will be in docs/diagrams/output/

""")
    
    print("💻 Opening browser in 3 seconds...")
    print("   (Waiting...)")
    
    import time
    time.sleep(3)
    
    # Open the HTML file in default browser
    file_url = html_file.as_uri()
    webbrowser.open(file_url)
    
    print(f"\n✅ Browser opened!")
    print(f"📁 HTML File: {html_file}")
    print(f"📁 Save PNG to: {output_dir.absolute()}")
    print(f"\n⏱️  This should take about 30 seconds total.")
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
