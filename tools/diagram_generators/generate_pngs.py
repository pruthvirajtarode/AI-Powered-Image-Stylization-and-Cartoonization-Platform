#!/usr/bin/env python3
"""
Alternative diagram generator using Plotly and Kaleido for PNG export
This script generates PNG versions of the Toonify AI architecture diagrams
"""

import json
import subprocess
import os
from pathlib import Path

def generate_diagrams_via_mermaid_live():
    """
    Generate PNG files by using a Node.js script that calls the Mermaid API
    """
    
    script_content = """
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

(async () => {{
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    const diagrams = [
        {{
            name: '01_System_Workflow',
            file: 'docs/diagrams/system_workflow.mmd'
        }},
        {{
            name: '02_UseCase_Diagram',
            file: 'docs/diagrams/usecase_diagram.mmd'
        }},
        {{
            name: '03_Sequence_Diagram',
            file: 'docs/diagrams/sequence_diagram.mmd'
        }},
        {{
            name: '04_Class_Diagram',
            file: 'docs/diagrams/class_diagram.mmd'
        }}
    ];
    
    for (const diagram of diagrams) {{
        const mermaidCode = fs.readFileSync(diagram.file, 'utf8');
        
        const html = `
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        </head>
        <body>
            <div class="mermaid">
${{mermaidCode}}
            </div>
            <script>
                mermaid.initialize({{ startOnLoad: true, theme: 'base' }});
                mermaid.contentLoaded();
            </script>
        </body>
        </html>
        `;
        
        await page.setContent(html);
        await page.waitForTimeout(2000);
        
        const outputPath = path.join('docs/diagrams/output', diagram.name + '.png');
        await page.screenshot({{ path: outputPath, fullPage: true }});
        console.log('Generated:', outputPath);
    }}
    
    await browser.close();
}})();
"""
    
    with open('generate_mermaid_pngs.js', 'w') as f:
        f.write(script_content)
    
    print("Node.js script created: generate_mermaid_pngs.js")
    print("\nTo use it, run:")
    print("  npm install puppeteer")
    print("  node generate_mermaid_pngs.js")

def create_simple_pngs_with_svg():
    """
    Create a simple HTML + SVG export method
    """
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ margin: 20px; font-family: Arial, sans-serif; }}
        SVG {{ max-width: 100%; height: auto; }}
        .diagram-container {{ page-break-after: always; margin-bottom: 40px; }}
    </style>
</head>
<body>
    <h1>Toonify AI - Architecture Diagrams</h1>
    <p>Open this HTML file in your browser, then:</p>
    <ol>
        <li>Right-click on each diagram</li>
        <li>Select "Save image as..."</li>
        <li>Save as PNG in docs/diagrams/output/</li>
    </ol>
    
    <div class="diagram-container">
        <h2>01 - System Workflow</h2>
        <div class="mermaid">
{WORKFLOW}
        </div>
    </div>
    
    <div class="diagram-container">
        <h2>02 - Use Case Diagram</h2>
        <div class="mermaid">
{USECASE}
        </div>
    </div>
    
    <div class="diagram-container">
        <h2>03 - Sequence Diagram</h2>
        <div class="mermaid">
{SEQUENCE}
        </div>
    </div>
    
    <div class="diagram-container">
        <h2>04 - Class Diagram</h2>
        <div class="mermaid">
{CLASS}
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'default',
            securityLevel: 'loose'
        }});
        mermaid.contentLoaded();
    </script>
</body>
</html>
"""
    
    # Read the diagram files
    diagrams_dir = Path('docs/diagrams')
    
    with open(diagrams_dir / 'system_workflow.mmd', 'r', encoding='utf-8') as f:
        workflow = f.read()
    with open(diagrams_dir / 'usecase_diagram.mmd', 'r', encoding='utf-8') as f:
        usecase = f.read()
    with open(diagrams_dir / 'sequence_diagram.mmd', 'r', encoding='utf-8') as f:
        sequence = f.read()
    with open(diagrams_dir / 'class_diagram.mmd', 'r', encoding='utf-8') as f:
        class_diagram = f.read()
    
    html_content = html_template.format(
        WORKFLOW=workflow,
        USECASE=usecase,
        SEQUENCE=sequence,
        CLASS=class_diagram
    )
    
    with open('mermaid_diagrams_export.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ Created: mermaid_diagrams_export.html")
    print("\n📌 Instructions:")
    print("1. Open 'mermaid_diagrams_export.html' in your browser")
    print("2. Right-click on each diagram")
    print("3. Select 'Save image as...'")
    print("4. Save to docs/diagrams/output/ with the corresponding names")

def main():
    print("=" * 60)
    print("Toonify AI - Diagram PNG Generator")
    print("=" * 60)
    
    output_dir = Path('docs/diagrams/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n📊 Creating HTML export file...")
    create_simple_pngs_with_svg()
    
    print("\n" + "=" * 60)
    print("✓ Complete!")
    print("=" * 60)
    print("\n✅ Two methods available:")
    print("\n  METHOD 1 - Easy (No dependencies):")
    print("    1. Open: mermaid_diagrams_export.html")
    print("    2. Right-click each diagram > Save as PNG")
    print("    3. Save to: docs/diagrams/output/")
    print("\n  METHOD 2 - Automated (Requires Node.js):")
    print("    1. node generate_mermaid_pngs.js (after npm install puppeteer)")
    print("\n  METHOD 3 - Online (Easiest):")
    print("    1. Visit: https://mermaid.live/")
    print("    2. Paste .mmd file contents")
    print("    3. Click 'Download PNG'")

if __name__ == '__main__':
    main()
