const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

(async () => {
    try {
        console.log('🎨 Starting Diagram PNG Generation...\n');
        
        const browser = await puppeteer.launch({ 
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        const diagrams = [
            {
                name: '01_System_Workflow',
                title: 'System Workflow'
            },
            {
                name: '02_UseCase_Diagram',
                title: 'Use Case Diagram'
            },
            {
                name: '03_Sequence_Diagram',
                title: 'Sequence Diagram'
            },
            {
                name: '04_Class_Diagram',
                title: 'Class Diagram'
            }
        ];
        
        // Create output directory
        const outputDir = path.join(__dirname, 'docs', 'diagrams', 'output');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        // Generate PNG for each diagram
        for (const diagram of diagrams) {
            console.log(`📊 Converting: ${diagram.title}...`);
            
            const htmlPath = path.join(__dirname, 'mermaid_diagrams_export.html');
            const fileUrl = `file://${htmlPath}`;
            
            await page.goto(fileUrl, { waitUntil: 'networkidle2' });
            
            // Wait for Mermaid to render
            await page.waitForSelector('.mermaid svg', { timeout: 5000 }).catch(() => {
                console.log('   ⚠️  SVG may not be visible, proceeding anyway...');
            });
            
            // Find the specific diagram section
            const diagramIndex = diagrams.indexOf(diagram);
            const sectionSelector = `.diagram-container:nth-of-type(${diagramIndex + 1})`;
            
            try {
                const element = await page.$(sectionSelector);
                if (element) {
                    const outputPath = path.join(outputDir, `${diagram.name}.png`);
                    await element.screenshot({ path: outputPath });
                    console.log(`   ✅ Saved: ${outputPath}`);
                } else {
                    console.log(`   ⚠️  Diagram section not found, trying full page...`);
                    const outputPath = path.join(outputDir, `${diagram.name}.png`);
                    await page.screenshot({ path: outputPath });
                    console.log(`   ✅ Saved: ${outputPath}`);
                }
            } catch (err) {
                console.log(`   ⚠️  Error capturing section: ${err.message}`);
                const outputPath = path.join(outputDir, `${diagram.name}.png`);
                await page.screenshot({ path: outputPath });
                console.log(`   ✅ Saved (full page): ${outputPath}`);
            }
        }
        
        await browser.close();
        
        console.log('\n' + '='.repeat(50));
        console.log('✅ All diagrams converted to PNG successfully!');
        console.log('='.repeat(50));
        console.log(`\n📁 Location: docs/diagrams/output/`);
        console.log('\n📋 Files created:');
        diagrams.forEach(d => {
            console.log(`   ✓ ${d.name}.png`);
        });
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
})();
