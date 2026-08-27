@echo off
REM Open diagrams in Chrome and allow manual PNG export

echo ============================================================
echo 🎨 Toonify AI - PNG Export via Chrome
echo ============================================================
echo.

REM Set paths
set CHROME_PATHS=^
    "C:\Program Files\Google\Chrome\Application\chrome.exe"^
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

REM Create output directory
if not exist "docs\diagrams\output" mkdir "docs\diagrams\output"
echo ✅ Output directory ready: docs\diagrams\output\
echo.

REM Find Chrome
set CHROME_CMD=
for %%i in (%CHROME_PATHS%) do (
    if exist %%i (
        set CHROME_CMD=%%i
        goto found_chrome
    )
)

:found_chrome
if "%CHROME_CMD%"=="" (
    echo ❌ Chrome not found! Install Chrome or use Method 2 below.
    goto manual_export
)

echo 📊 Opening HTML diagrams in Chrome...
echo.
echo Step 1: Browser will open shortly
echo Step 2: Right-click each diagram
echo Step 3: Select "Save image as..."
echo Step 4: Save to: docs\diagrams\output\
echo.
echo File names to use:
echo  • 01_System_Workflow.png
echo  • 02_UseCase_Diagram.png
echo  • 03_Sequence_Diagram.png
echo  • 04_Class_Diagram.png
echo.

timeout /t 2 >nul

REM Get absolute path
cd /d "%~dp0"
for /f %%i in ('cd') do set FULL_PATH=%%i
set HTML_FILE=%FULL_PATH%\mermaid_diagrams_export.html

REM Open in Chrome
start "" "%CHROME_CMD%" "file:///%HTML_FILE%"

echo ✅ Chrome opened! Follow the steps above.
echo.
goto end

:manual_export
echo.
echo ============================================================
echo Method 2: Manual Export (Online)
echo ============================================================
echo.
echo 1. Visit: https://mermaid.live/
echo 2. Open each .mmd file from: docs\diagrams\
echo 3. Copy the code into Mermaid Live
echo 4. Click "Download" button
echo 5. Choose PNG format
echo 6. Save to: docs\diagrams\output\
echo.

:end
echo ============================================================
pause
