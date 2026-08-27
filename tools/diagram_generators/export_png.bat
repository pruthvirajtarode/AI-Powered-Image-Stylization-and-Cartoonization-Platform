@echo off
REM Open diagrams in Chrome for manual PNG export

setlocal enabledelayedexpansion

echo ============================================================
echo 🎨 Toonify AI - PNG Export
echo ============================================================
echo.

REM Create output directory
if not exist "docs\diagrams\output" mkdir "docs\diagrams\output"
echo OK Output directory ready: docs\diagrams\output
echo.

REM Find Chrome
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
)
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files ^(x86^)\Google\Chrome\Application\chrome.exe
)

if "!CHROME_PATH!"=="" (
    echo Chrome not found. Using method 2 instead.
    goto manual_export
)

echo Opening diagrams in Chrome...
echo.
echo INSTRUCTIONS:
echo 1. Browser will open shortly
echo 2. Right-click each diagram
echo 3. Select "Save image as"
echo 4. Choose PNG format
echo 5. Save to: docs\diagrams\output
echo.
echo File names:
echo - 01_System_Workflow.png
echo - 02_UseCase_Diagram.png
echo - 03_Sequence_Diagram.png
echo - 04_Class_Diagram.png
echo.

timeout /t 2 >nul

set HTML_FILE=%CD%\mermaid_diagrams_export.html
start "" "!CHROME_PATH!" "file:///!HTML_FILE!"

echo OK Opening Chrome...
goto done

:manual_export
echo.
echo METHOD 2 - Online Export
echo Visit: https://mermaid.live
echo Upload .mmd files and download PNG
echo.

:done
echo ============================================================
pause
