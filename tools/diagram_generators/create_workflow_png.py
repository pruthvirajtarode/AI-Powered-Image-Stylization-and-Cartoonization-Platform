#!/usr/bin/env python3
"""
Create system_workflow.png using Pillow with diagram text
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_workflow_png():
    """Create a diagram PNG file"""
    
    # Create image
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        header_font = ImageFont.truetype("arial.ttf", 32)
        text_font = ImageFont.truetype("arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Colors
    color_bg = '#f8f9fa'
    color_text = '#333333'
    color_header = '#667eea'
    color_accent = '#764ba2'
    
    # Draw title
    draw.text((60, 50), "Toonify AI - System Workflow", fill=color_header, font=title_font)
    
    # Draw workflow steps
    y_pos = 150
    steps = [
        "1. User Uploads Image → Authentication (OAuth 2.0)",
        "2. Session Verification → Premium User Check",
        "3. Image Validation → Quality Selection (Standard/Premium 4K)",
        "4. Select AI Style (Pixar, Anime, Comic, Oil Paint, etc.)",
        "5. Image Processing Engine → OpenCV + Neural Networks",
        "6. Apply Neural Style Transformation",
        "7. Success Check → Cache Thumbnail & Store in Database",
        "8. Export Options: WhatsApp, Instagram, or Direct Download",
        "9. Analytics Tracking → Update Creator Dashboard",
        "10. Process Complete",
    ]
    
    for step in steps:
        draw.text((100, y_pos), step, fill=color_text, font=text_font)
        y_pos += 60
    
    # Save as PNG
    output_path = Path('docs/diagrams/output/01_System_Workflow.png')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')
    
    size_kb = output_path.stat().st_size / 1024
    print(f'✅ Created: {output_path} ({size_kb:.1f} KB)')
    return True

if __name__ == '__main__':
    print('Creating system_workflow.png...')
    try:
        create_workflow_png()
        print('\n✅ All 4 PNG files now complete!')
        print('📁 Location: docs/diagrams/output/')
    except Exception as e:
        print(f'❌ Error: {e}')
