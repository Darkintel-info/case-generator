@echo off
REM =============================================================================
REM Case Generator v2.0 - Windows Build Script
REM Dark Intel, Inc | www.darkintel.info
REM
REM Double-click this file to build CaseGenerator.exe
REM Requirements: Python 3.10+
REM =============================================================================

echo.
echo ============================================================
echo   Case Generator v2.0 - Windows Executable Builder
echo   Dark Intel, Inc  ^|  www.darkintel.info
echo ============================================================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [2/3] Installing PyInstaller...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [3/3] Building CaseGenerator.exe...
echo.
python -m PyInstaller case_generator.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD SUCCESSFUL
echo ============================================================
echo.
echo   Executable location:
echo   %~dp0dist\CaseGenerator.exe
echo.
echo   The .exe is a single self-contained file.
echo   Copy CaseGenerator.exe to any Windows machine and run it.
echo   No Python installation required on the target machine.
echo.

REM Open the dist folder in Explorer
explorer "%~dp0dist"

pause
