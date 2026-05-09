@echo off
cd /d "%~dp0"
echo Using portable Python...
echo Financial Assistant: http://127.0.0.1:18765
echo Press Ctrl+C to stop.
".python\python.exe" "server.py"
pause
