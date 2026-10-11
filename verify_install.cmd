@echo off
setlocal
cd /d "%~dp0"
python -B "%~dp0src\verify_install.py"
exit /b %errorlevel%
