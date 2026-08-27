#!/usr/bin/env python3
"""
Script to generate PNG diagrams from Mermaid markdown files
Requires: pip install mmdc (or use online Mermaid service)
"""

import os
import subprocess
import sys
from pathlib import Path

def convert_mermaid_to_png():
    """Convert Mermaid markdown files to PNG format"""
    
    diagrams_dir = Path("docs/diagrams")
    output_dir = Path("docs/diagrams/output")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # List of diagram files to convert
    diagrams = [
        ("docs/diagrams/system_workflow.md", "docs/diagrams/output/01_System_Workflow.png"),
        ("docs/diagrams/usecase_diagram.md", "docs/diagrams/output/02_UseCase_Diagram.png"),
        ("docs/diagrams/sequence_diagram.md", "docs/diagrams/output/03_Sequence_Diagram.png"),
        ("docs/diagrams/class_diagram.md", "docs/diagrams/output/04_Class_Diagram.png"),
    ]
    
    print("🎨 Toonify AI Diagram Generator")
    print("=" * 50)
    
    # Method 1: Try using mermaid-cli (mmdc)
    try:
        print("\n📦 Attempting to use mermaid-cli (mmdc)...")
        for md_file, png_file in diagrams:
            if os.path.exists(md_file):
                print(f"✓ Converting: {md_file}")
                subprocess.run(
                    ["mmdc", "-i", md_file, "-o", png_file, "-w", "1920", "-H", "1080"],
                    check=True
                )
                print(f"  ✓ Saved: {png_file}")
        return True
    except FileNotFoundError:
        print("⚠️  mermaid-cli not found. Trying alternative method...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error with mermaid-cli: {e}")
    
    # Method 2: Extract Mermaid code and provide online conversion instructions
    print("\n📋 Alternative: Online Conversion Instructions")
    print("=" * 50)
    print("\nSince mermaid-cli is not available, use one of these methods:\n")
    
    print("METHOD 1️⃣ : Using Mermaid Online Editor")
    print("-" * 50)
    print("1. Go to: https://mermaid.live/")
    print("2. Paste the Mermaid code from any .md file in docs/diagrams/")
    print("3. Click 'Download PNG'")
    print("\n")
    
    print("METHOD 2️⃣ : Using Docker (if installed)")
    print("-" * 50)
    print("docker run --rm -v $(pwd):/data minlag/mermaid-cli \\")
    print("  -i /data/docs/diagrams/system_workflow.md \\")
    print("  -o /data/docs/diagrams/output/01_System_Workflow.png")
    print("\n")
    
    print("METHOD 3️⃣ : Install mermaid-cli locally")
    print("-" * 50)
    print("npm install -g mermaid-cli")
    print("Then run this script again: python generate_diagrams.py")
    print("\n")
    
    print("📁 Mermaid Files Location:")
    print("-" * 50)
    for md_file, _ in diagrams:
        if os.path.exists(md_file):
            print(f"✓ {md_file}")
        else:
            print(f"✗ {md_file} (not found)")
    
    return False

def create_html_viewer():
    """Create an HTML file to view diagrams in browser"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toonify AI - Architecture Diagrams</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .diagrams-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .diagram-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .diagram-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
        }
        
        .diagram-card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .diagram-card p {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .mermaid {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
        }
        
        .diagram-buttons {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-download {
            background: #667eea;
            color: white;
        }
        
        .btn-download:hover {
            background: #5568d3;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        @media (max-width: 768px) {
            .diagrams-grid {
                grid-template-columns: 1fr;
            }
            
            header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎨 Toonify AI - Architecture Diagrams</h1>
            <p>Complete system architecture visualization</p>
        </header>
        
        <div class="diagrams-grid">
            <div class="diagram-card">
                <h2>📊 System Workflow</h2>
                <p>Complete journey of an image through the Toonify AI system, from upload through processing to delivery.</p>
                <div class="mermaid">
graph TD
    A["👤 User Uploads Image"] --> B{"Authenticated?"}
    B -->|No| C["OAuth 2.0 Login"]
    C --> D["Session Created"]
    B -->|Yes| E["Validate Image"]
    D --> E
    E -->|Invalid| F["Return Error"]
    E -->|Valid| G{"Premium User?"}
    G -->|No| H["4K Disabled<br/>Standard Quality"]
    G -->|Yes| I["4K Enabled<br/>Premium Quality"]
    H --> J["Select AI Style"]
    I --> J
    J --> K["Image Processing<br/>Engine"]
    K --> L["OpenCV + AI Models"]
    L --> M["Apply Neural Style"]
    M --> N{"Processing<br/>Successful?"}
    N -->|Failed| O["Error Logging & Return"]
    N -->|Success| P["Cache Thumbnail"]
    P --> Q["Store in DB"]
    Q --> R{"Export Request?"}
    R -->|WhatsApp| S["WhatsApp API"]
    R -->|Download| U["Send File"]
    S --> V["User Receives<br/>Stylized Image"]
    U --> V
    V --> W["Analytics Tracking"]
    W --> X["✨ Complete"]
                </div>
            </div>
            
            <div class="diagram-card">
                <h2>🎭 Use Case Diagram</h2>
                <p>Different user roles (Free, Premium, Admin) and their interactions with system features and external services.</p>
                <div class="mermaid">
graph TB
    subgraph Users
        U1["👤 Free User"]
        U2["💳 Premium User"]
        U3["⚙️ Admin"]
    end
    
    subgraph System["🎨 Toonify AI"]
        UC1["Upload Image"]
        UC4["Download Result"]
        UC5["Share on Social"]
    end
    
    subgraph External["External Services"]
        E1["Google OAuth"]
        E2["Razorpay"]
        E3["WhatsApp"]
    end
    
    U1 --> UC1
    U2 --> UC1
    U2 --> UC4
    U2 --> UC5
    U3 --> E2
    
    UC1 --> E1
    UC5 --> E3
                </div>
            </div>
            
            <div class="diagram-card">
                <h2>🔄 Sequence Diagram</h2>
                <p>Step-by-step interaction flow between frontend, backend, and services during image processing and export.</p>
                <div class="mermaid">
sequenceDiagram
    participant User as 👤 User
    participant Frontend as 🖥️ Frontend
    participant Flask as 🚀 Backend
    participant Auth as 🔐 Auth
    participant ImageProc as 🎨 Processor
    
    User->>Frontend: Upload Image
    Frontend->>Flask: POST /upload
    Flask->>Auth: Verify Session
    Auth-->>Flask: ✓ Authenticated
    
    User->>Frontend: Select Style
    Frontend->>Flask: POST /process
    Flask->>ImageProc: Apply Style
    ImageProc-->>Flask: Result
    
    Frontend-->>User: Display Image
                </div>
            </div>
            
            <div class="diagram-card">
                <h2>🏗️ Class Diagram</h2>
                <p>Core system components and their relationships: Flask App, Authentication, Image Processing, Database, and integrations.</p>
                <div class="mermaid">
classDiagram
    class Flask_App {
        +route_upload()
        +route_process()
        +route_download()
    }
    
    class Authentication {
        +google_login()
        +hash_password()
    }
    
    class ImageProcessor {
        +load_image()
        +process_style()
    }
    
    class Database {
        +create_user()
        +save_record()
    }
    
    class User {
        -id int
        -email str
        -plan str
    }
    
    Flask_App --|> Authentication
    Flask_App --|> ImageProcessor
    Flask_App --|> Database
    Database --|> User
                </div>
            </div>
        </div>
        
        <footer>
            <p>🔗 For high-resolution PNG files, see: <strong>docs/diagrams/</strong> directory</p>
            <p>📖 Architecture documentation available in the project docs</p>
        </footer>
    </div>
    
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'default' });
        mermaid.contentLoaded();
    </script>
</body>
</html>
"""
    
    with open("diagram_viewer.html", "w") as f:
        f.write(html_content)
    
    print("\n✅ HTML Viewer created: diagram_viewer.html")
    print("   Open in browser to view all diagrams interactively!")

if __name__ == "__main__":
    print("\n")
    success = convert_mermaid_to_png()
    
    # Always create HTML viewer
    create_html_viewer()
    
    if success:
        print("\n✅ All diagrams converted successfully!")
        print("📁 Check: docs/diagrams/output/")
    else:
        print("\n💡 Diagrams are ready to convert. Choose a method above!")
        print("📄 Or open: diagram_viewer.html in your browser")
    
    print("\n" + "=" * 50)
