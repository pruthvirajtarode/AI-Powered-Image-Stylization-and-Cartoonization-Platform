#!/usr/bin/env python3
"""
Convert Mermaid diagrams HTML to PNG using WeasyPrint (simplified)
"""

from pathlib import Path
import sys

def convert_html_to_png():
    """Convert the HTML file to PNG"""
    try:
        from weasyprint import HTML
        
        print("="*70)
        print("🎨 Converting HTML Diagram to PNG")
        print("="*70 + "\n")
        
        html_file = Path('mermaid_diagrams_export.html')
        output_dir = Path('docs/diagrams/output')
        
        if not html_file.exists():
            print(f"❌ Error: {html_file} not found!")
            return False
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert HTML to PNG
        output_file = output_dir / 'toonify_ai_diagrams_all.png'
        
        print(f"📄 Input file: {html_file}")
        print(f"📁 Output directory: {output_dir.absolute()}")
        print(f"📊 Converting to PNG...")
        print(f"   (This may take 10-30 seconds)\n")
        
        HTML(string=open(html_file).read()).write_png(output_file)
        
        file_size_kb = output_file.stat().st_size / 1024
        print(f"\n✅ Conversion successful!")
        print(f"📁 Saved: {output_file}")
        print(f"💾 Size: {file_size_kb:.1f} KB")
        print(f"\n✨ Advanced: For individual diagrams, use:")
        print(f"   - Mermaid.live online editor")
        print(f"   - Right-click diagrams in browser > Save as PNG")
        
        return True
        
    except ImportError:
        print("❌ WeasyPrint not installed")
        print("   Run: pip install weasyprint")
        return False
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False

if __name__ == '__main__':
    success = convert_html_to_png()
    sys.exit(0 if success else 1)
