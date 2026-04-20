#!/usr/bin/env python3
"""
Generate PNG from Mermaid diagrams using mermaid.ink service
"""

import urllib.request
import urllib.parse
import base64
import json
from pathlib import Path
import time

def generate_png_from_mermaid(mmd_file, png_file):
    """Convert a Mermaid file to PNG using mermaid.ink API"""
    
    try:
        # Read the Mermaid diagram code
        with open(mmd_file, 'r', encoding='utf-8') as f:
            diagram_code = f.read().strip()
        
        print(f'📊 Processing: {mmd_file}')
        print(f'   Code length: {len(diagram_code)} bytes')
        
        # Use mermaid.ink rendering API
        # Format: https://mermaid.ink/svg/[base64-encoded-diagram]
        
        # Encode the diagram code in base64
        encoded = base64.b64encode(diagram_code.encode()).decode('ascii')
        
        # Try method 1: mermaid.ink
        print(f'   Rendering...')
        url = f'https://mermaid.ink/img/{encoded}'
        
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                image_data = response.read()
                
                # Save the PNG
                Path(png_file).parent.mkdir(parents=True, exist_ok=True)
                with open(png_file, 'wb') as f:
                    f.write(image_data)
                
                size_kb = len(image_data) / 1024
                print(f'   ✅ Saved: {png_file} ({size_kb:.1f} KB)\n')
                return True
                
        except Exception as e1:
            print(f'   ⚠️  mermaid.ink failed: {str(e1)[:50]}')
            
            # Try method 2: kroki.io SVG then convert
            print(f'   Trying alternative service...')
            try:
                kroki_url = f'https://kroki.io/mermaid/png/{encoded}'
                req = urllib.request.Request(
                    kroki_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    image_data = response.read()
                    
                    Path(png_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(png_file, 'wb') as f:
                        f.write(image_data)
                    
                    size_kb = len(image_data) / 1024
                    print(f'   ✅ Saved via kroki: {png_file} ({size_kb:.1f} KB)\n')
                    return True
            except Exception as e2:
                print(f'   ❌ Both methods failed\n')
                return False
    
    except Exception as e:
        print(f'❌ Error: {e}\n')
        return False

def main():
    print('='*70)
    print('🎨 Toonify AI - PNG Generator (API Method)')
    print('='*70)
    print()
    
    diagrams = [
        ('docs/diagrams/system_workflow.mmd', 'docs/diagrams/output/01_System_Workflow.png'),
        ('docs/diagrams/usecase_diagram.mmd', 'docs/diagrams/output/02_UseCase_Diagram.png'),
        ('docs/diagrams/sequence_diagram.mmd', 'docs/diagrams/output/03_Sequence_Diagram.png'),
        ('docs/diagrams/class_diagram.mmd', 'docs/diagrams/output/04_Class_Diagram.png'),
    ]
    
    success_count = 0
    failed_count = 0
    
    for mmd_file, png_file in diagrams:
        if Path(mmd_file).exists():
            if generate_png_from_mermaid(mmd_file, png_file):
                success_count += 1
            else:
                failed_count += 1
            time.sleep(1)  # Rate limiting
        else:
            print(f'❌ File not found: {mmd_file}\n')
            failed_count += 1
    
    print('='*70)
    if success_count == 4:
        print(f'✅ SUCCESS! All 4 PNG files generated!')
        print('📁 Location: docs/diagrams/output/')
        print()
        print('Files created:')
        for _, png_file in diagrams:
            if Path(png_file).exists():
                size = Path(png_file).stat().st_size / 1024
                print(f'   ✓ {Path(png_file).name} ({size:.1f} KB)')
    else:
        print(f'⚠️  Partial success: {success_count} generated, {failed_count} failed')
        if failed_count > 0:
            print('\n📋 For failed diagrams, use the browser method:')
            print('   1. Open: mermaid_diagrams_export.html')
            print('   2. Right-click diagram → Save as PNG')
    print('='*70)

if __name__ == '__main__':
    main()
