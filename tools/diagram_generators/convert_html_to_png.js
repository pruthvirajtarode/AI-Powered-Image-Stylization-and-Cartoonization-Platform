#!/usr/bin/env node

/**
 * Convert Mermaid diagrams from HTML to PNG using Playwright
 * Install: npm install -g playwright
 */

const fs = require('fs');
const path = require('path');

async function convertToPNG() {
    console.log('='.repeat(70));
    console.log('🎨 Toonify AI - PNG Diagram Generator');
    console.log('='.repeat(70));
    console.log('');

    try {
        // Try importing playwright
        let playwright;
        try {
            playwright = require('playwright');
        } catch (e) {
            console.error('❌ Playwright not installed');
            console.log('\n📦 Install with: npm install -g playwright');
            process.exit(1);
        }

        const browser = await playwright.chromium.launch();
        const page = await browser.newPage();

        const htmlFile = path.join(__dirname, 'mermaid_diagrams_export.html');
        const outputDir = path.join(__dirname, 'docs', 'diagrams', 'output');

        // Ensure output directory exists
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        console.log('📄 HTML File:', htmlFile);
        console.log('📁 Output Dir:', outputDir);
        console.log('');

        // Navigate to the HTML file
        await page.goto(`file://${htmlFile}`, { waitUntil: 'networkidle' });

        // Wait for Mermaid to render
        await page.waitForTimeout(3000);

        const diagrams = [
            { selector: '.diagram-container:nth-of-type(1)', name: '01_System_Workflow.png' },
            { selector: '.diagram-container:nth-of-type(2)', name: '02_UseCase_Diagram.png' },
            { selector: '.diagram-container:nth-of-type(3)', name: '03_Sequence_Diagram.png' },
            { selector: '.diagram-container:nth-of-type(4)', name: '04_Class_Diagram.png' },
        ];

        console.log('📊 Converting diagrams...\n');

        for (const diagram of diagrams) {
            try {
                const element = await page.$(diagram.selector);
                if (element) {
                    const outputPath = path.join(outputDir, diagram.name);
                    await element.screenshot({ path: outputPath });
                    const size = fs.statSync(outputPath).size / 1024;
                    console.log(`✅ ${diagram.name} (${size.toFixed(1)} KB)`);
                } else {
                    console.log(`⚠️  ${diagram.name} - Selector not found`);
                }
            } catch (err) {
                console.log(`❌ ${diagram.name} - Error: ${err.message}`);
            }
        }

        await browser.close();

        console.log('\n' + '='.repeat(70));
        console.log('✅ PNG conversion completed!');
        console.log('='.repeat(70));
        console.log(`📁 Location: ${outputDir}`);

    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

convertToPNG();
