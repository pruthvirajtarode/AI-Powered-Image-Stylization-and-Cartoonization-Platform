@echo off
REM Convert Mermaid diagrams to PNG on Windows
REM Requires: npm install -g mermaid-cli

echo 🎨 Toonify AI Diagram Converter (Windows)
echo =========================================

REM Check if mmdc is available
where mmdc >nul 2>nul
if %errorlevel% equ 0 (
    echo ✓ Found mermaid-cli
    
    if not exist docs\diagrams\output mkdir docs\diagrams\output
    
    echo Converting diagrams...
    mmdc -i docs/diagrams/system_workflow.md -o docs/diagrams/output/01_System_Workflow.png -w 1920 -H 1080
    mmdc -i docs/diagrams/usecase_diagram.md -o docs/diagrams/output/02_UseCase_Diagram.png -w 1920 -H 1080
    mmdc -i docs/diagrams/sequence_diagram.md -o docs/diagrams/output/03_Sequence_Diagram.png -w 1920 -H 1080
    mmdc -i docs/diagrams/class_diagram.md -o docs/diagrams/output/04_Class_Diagram.png -w 1920 -H 1080
    
    echo ✓ All diagrams converted successfully!
    echo 📁 Check: docs\diagrams\output\
    pause
) else (
    echo ⚠️  mermaid-cli not found
    echo.
    echo Install options:
    echo 1. npm install -g mermaid-cli
    echo 2. Or visit: https://mermaid.live/
    echo.
    echo After installing mermaid-cli, run this script again.
    pause
)
