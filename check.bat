@echo off
setlocal
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1

echo ============================================
echo  ART-12D  -  verificare completa PASS/FAIL
echo ============================================
echo.

python -u check.py %*
set RC=%ERRORLEVEL%
echo.
pause
endlocal
