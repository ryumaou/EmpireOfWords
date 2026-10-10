@echo off
setlocal
cd /d "%~dp0"
echo Checking translator location and version...
python "%~dp0src\translate.py" --version
if errorlevel 1 (echo FAILED: Python or translator is unavailable.& exit /b 1)
echo Expected: Empire Of Words translator 7.6.0
echo To translate, run commands from this directory.
endlocal
