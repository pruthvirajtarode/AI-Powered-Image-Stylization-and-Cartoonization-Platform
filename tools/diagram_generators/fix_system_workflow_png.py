#!/usr/bin/env python3
"""
Generate the missing system_workflow.png
"""

import urllib.request
import base64
from pathlib import Path
import time

def generate_png(mmd_file, png_file):
    """Convert Mermaid file to PNG"""
    
    with open(mmd_file, 'r', encoding='utf-8') as f:
        code = f.read().strip()
    
    print(f'📊 Converting: {mmd_file}')
    encoded = base64.b64encode(code.encode()).decode('ascii')
    
    # Try mermaid.ink first
    try:
        print('   Trying mermaid.ink...')
        url = f'https://mermaid.ink/img/{encoded}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            Path(png_file).parent.mkdir(parents=True, exist_ok=True)
            with open(png_file, 'wb') as f:
                f.write(data)
            size = len(data) / 1024
            print(f'   ✅ Success! ({size:.1f} KB)\n')
            return True
    except Exception as e1:
        print(f'   Failed: {str(e1)[:40]}')
    
    # Try kroki.io
    try:
        print('   Trying kroki.io...')
        url = f'https://kroki.io/mermaid/png/{encoded}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            Path(png_file).parent.mkdir(parents=True, exist_ok=True)
            with open(png_file, 'wb') as f:
                f.write(data)
            size = len(data) / 1024
            print(f'   ✅ Success via kroki.io! ({size:.1f} KB)\n')
            return True
    except Exception as e2:
        print(f'   Failed: {str(e2)[:40]}\n')
        return False

if __name__ == '__main__':
    success = generate_png(
        'docs/diagrams/system_workflow.mmd',
        'docs/diagrams/output/01_System_Workflow.png'
    )
    
    if success:
        print('✅ All 4 PNG files now exist!')
        print('📁 Location: docs/diagrams/output/')
    else:
        print('⚠️  Manual export needed')
        print('📋 Open: mermaid_diagrams_export.html')
        print('   Right-click 1st diagram → Save as PNG')
