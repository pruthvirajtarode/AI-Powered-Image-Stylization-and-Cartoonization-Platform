#!/bin/bash
# Convert Mermaid diagrams to PNG using Docker or mermaid-cli

echo "🎨 Toonify AI Diagram Converter"
echo "================================="

# Check if mmdc is available
if command -v mmdc &> /dev/null; then
    echo "✓ Found mermaid-cli"
    mkdir -p docs/diagrams/output
    
    mmdc -i docs/diagrams/system_workflow.md -o docs/diagrams/output/01_System_Workflow.png -w 1920 -H 1080
    mmdc -i docs/diagrams/usecase_diagram.md -o docs/diagrams/output/02_UseCase_Diagram.png -w 1920 -H 1080
    mmdc -i docs/diagrams/sequence_diagram.md -o docs/diagrams/output/03_Sequence_Diagram.png -w 1920 -H 1080
    mmdc -i docs/diagrams/class_diagram.md -o docs/diagrams/output/04_Class_Diagram.png -w 1920 -H 1080
    
    echo "✓ All diagrams converted successfully!"
else
    echo "⚠️  mermaid-cli not found"
    echo ""
    echo "Install options:"
    echo "1. npm install -g mermaid-cli"
    echo "2. Or use Docker: docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/docs/diagrams/*.md -o /data/docs/diagrams/output/"
    echo "3. Or use online: https://mermaid.live/"
fi
