#!/usr/bin/env python3
"""
Generate PNG files from Mermaid diagrams using SVG conversion
"""

import subprocess
import sys
from pathlib import Path
import json

def install_package(package):
    """Install a package using pip"""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])

def generate_pngs_via_mermaid_cli():
    """Try using system mermaid or node-based mermaid-cli"""
    try:
        # Check if mmdc (mermaid-cli) is available
        subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
        print('✅ Found mermaid-cli')
        
        diagrams = [
            ('docs/diagrams/system_workflow.mmd', 'docs/diagrams/output/01_System_Workflow.png'),
            ('docs/diagrams/usecase_diagram.mmd', 'docs/diagrams/output/02_UseCase_Diagram.png'),
            ('docs/diagrams/sequence_diagram.mmd', 'docs/diagrams/output/03_Sequence_Diagram.png'),
            ('docs/diagrams/class_diagram.mmd', 'docs/diagrams/output/04_Class_Diagram.png'),
        ]
        
        for mmd_file, png_file in diagrams:
            if Path(mmd_file).exists():
                print(f'📊 Converting: {mmd_file}...')
                try:
                    subprocess.run([
                        'mmdc', 
                        '-i', mmd_file, 
                        '-o', png_file,
                        '-w', '1920',
                        '-H', '1080'
                    ], check=True, timeout=30)
                    size_kb = Path(png_file).stat().st_size / 1024
                    print(f'   ✅ Saved: {png_file} ({size_kb:.1f} KB)')
                except Exception as e:
                    print(f'   ❌ Failed: {e}')
        
        return True
    except:
        return False

def generate_pngs_via_api():
    """Generate PNGs using online Mermaid rendering API"""
    try:
        import requests
        import base64
        
        print('📡 Using Mermaid API for PNG generation...\n')
        
        diagrams = {
            'docs/diagrams/system_workflow.mmd': 'docs/diagrams/output/01_System_Workflow.png',
            'docs/diagrams/usecase_diagram.mmd': 'docs/diagrams/output/02_UseCase_Diagram.png',
            'docs/diagrams/sequence_diagram.mmd': 'docs/diagrams/output/03_Sequence_Diagram.png',
            'docs/diagrams/class_diagram.mmd': 'docs/diagrams/output/04_Class_Diagram.png',
        }
        
        Path('docs/diagrams/output').mkdir(parents=True, exist_ok=True)
        
        for mmd_file, png_file in diagrams.items():
            if Path(mmd_file).exists():
                print(f'📊 Converting: {mmd_file}...')
                
                # Read diagram code
                with open(mmd_file, 'r', encoding='utf-8') as f:
                    diagram_code = f.read()
                
                # Use Mermaid rendering service
                try:
                    # Try using kroki.io (free online diagram renderer)
                    encoded = base64.b64encode(diagram_code.encode()).decode()
                    url = f'https://kroki.io/mermaid/png/{encoded}'
                    
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(png_file, 'wb') as f:
                            f.write(response.content)
                        size_kb = Path(png_file).stat().st_size / 1024
                        print(f'   ✅ Saved: {png_file} ({size_kb:.1f} KB)')
                    else:
                        print(f'   ⚠️  API error: {response.status_code}')
                except Exception as e:
                    print(f'   ❌ Failed: {e}')
        
        return True
    except ImportError:
        print('❌ requests library not available')
        return False

def create_manual_export_guide():
    """Create comprehensive manual export instructions"""
    
    print('\n' + '='*70)
    print('🎯 MANUAL PNG EXPORT GUIDE')
    print('='*70)
    
    guide = """
Since automated conversion is not available, here's how to get your PNGs:

═══════════════════════════════════════════════════════════════════════════

METHOD 1: BROWSER EXPORT (FASTEST - 3 minutes)
─────────────────────────────────────────────

1️⃣  Open this file in your browser:
   → mermaid_diagrams_export.html

2️⃣  For EACH diagram (4 total):
   
   Step 1: Right-click on the diagram
   Step 2: Select "Save image as..."
   Step 3: Name it exactly:
           
           01_System_Workflow.png
           02_UseCase_Diagram.png
           03_Sequence_Diagram.png
           04_Class_Diagram.png
   
   Step 4: Save to: docs\\diagrams\\output\\

3️⃣  Done! You now have 4 PNG files.

═══════════════════════════════════════════════════════════════════════════

METHOD 2: ONLINE EDITOR (EASIEST)
────────────────────────────────

1️⃣  Go to: https://mermaid.live/

2️⃣  For EACH diagram:
   
   a) Open file from: docs/diagrams/
      (Example: system_workflow.mmd)
   
   b) Copy entire contents into Mermaid Live editor
   
   c) Click "Download" button
   
   d) Save as PNG with correct name
   
   e) Save to: docs/diagrams/output/

3️⃣  Repeat for all 4 diagrams

═══════════════════════════════════════════════════════════════════════════

DIAGRAM FILES & OUTPUT NAMES:

Input File                      →  Output PNG
─────────────────────────────────────────────────────────────
system_workflow.mmd             →  01_System_Workflow.png
usecase_diagram.mmd             →  02_UseCase_Diagram.png
sequence_diagram.mmd            →  03_Sequence_Diagram.png
class_diagram.mmd               →  04_Class_Diagram.png

═══════════════════════════════════════════════════════════════════════════

SAVE LOCATION:

   docs\\diagrams\\output\\
   
   Example full path:
   C:\\Users\\pruth\\OneDrive\\Desktop\\AI-Powered Image Stylization and Cartoonization Platform\\docs\\diagrams\\output\\01_System_Workflow.png

═══════════════════════════════════════════════════════════════════════════

✨ RECOMMENDED: Use METHOD 1 (Browser Export)
   ✅ No installation needed
   ✅ Works on any computer
   ✅ Full quality control
   ✅ Takes only 3 minutes total
   ✅ Just 4 right-clicks!

═══════════════════════════════════════════════════════════════════════════
"""
    
    print(guide)
    
    # Save guide to file
    with open('PNG_MANUAL_EXPORT_GUIDE.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print('\n📄 Guide saved to: PNG_MANUAL_EXPORT_GUIDE.txt')

def main():
    print('='*70)
    print('🎨 Toonify AI - PNG Diagram Generator')
    print('='*70)
    print()
    
    # Try automated methods
    print('📊 Attempting automated PNG generation...\n')
    
    # Method 1: Try mermaid-cli
    if generate_pngs_via_mermaid_cli():
        print('\n✅ PNG files generated successfully!')
        return
    
    print('⚠️  mermaid-cli not available\n')
    
    # Method 2: Try online API
    print('📦 Installing requests library...')
    try:
        install_package('requests')
        if generate_pngs_via_api():
            print('\n✅ PNG files generated using online API!')
            return
    except:
        print('⚠️  API method not available\n')
    
    # Fallback: manual guide
    print('ℹ️  Automated conversion not available')
    print('📋 Showing manual export guide instead...\n')
    create_manual_export_guide()

if __name__ == '__main__':
    main()
