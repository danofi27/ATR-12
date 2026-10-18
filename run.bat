@echo off
setlocal
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1

echo ============================================
echo  ART-12D  -  rulare simulare
echo ============================================
echo.

python -c "import numpy, scipy, matplotlib" 2>nul
if errorlevel 1 (
    echo Lipsesc pachete. Rulez: pip install -r requirements.txt
    python -m pip install -r requirements.txt
    echo.
)

python -u run_atr12.py %*
set RC=%ERRORLEVEL%
echo.
if %RC%==0 (
    echo Gata. Deschide results\atr12_report.md si figures\
) else (
    echo Rularea s-a terminat cu codul %RC%.
)
echo.
pause
endlocal
