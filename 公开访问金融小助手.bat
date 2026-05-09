@echo off
setlocal
cd /d "%~dp0"

set "PORT=18765"
set "LOCAL_URL=http://127.0.0.1:%PORT%"
set "PYTHON_EXE=%~dp0.python\python.exe"
set "SERVER_FILE=%~dp0server.py"
set "CLOUDFLARED_EXE=%~dp0cloudflared.exe"

title Financial Assistant Public Link
echo.
echo ============================================================
echo  Financial Assistant - Public Access
echo ============================================================
echo.
echo This window will create a free temporary Cloudflare link.
echo Keep this window open. If you close it, the public link stops.
echo.

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Portable Python was not found:
  echo %PYTHON_EXE%
  echo.
  echo Please run the local version first.
  pause
  exit /b 1
)

if not exist "%SERVER_FILE%" (
  echo [ERROR] server.py was not found:
  echo %SERVER_FILE%
  pause
  exit /b 1
)

if not exist "%CLOUDFLARED_EXE%" (
  echo [ERROR] cloudflared.exe was not found:
  echo %CLOUDFLARED_EXE%
  echo.
  echo Download it from:
  echo https://developers.cloudflare.com/tunnel/downloads/
  pause
  exit /b 1
)

echo Checking local service: %LOCAL_URL%
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing '%LOCAL_URL%/' -TimeoutSec 2; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul

if errorlevel 1 (
  echo Local service is not running. Starting Python server...
  start "Financial Assistant Local Server" /min "%PYTHON_EXE%" "%SERVER_FILE%"
  timeout /t 4 /nobreak >nul
) else (
  echo Local service is already running.
)

echo.
echo Creating public URL...
echo.
echo Look for a line like:
echo   https://xxxx.trycloudflare.com
echo.
echo Send that URL to other people.
echo Press Ctrl+C in this window to stop public access.
echo.

"%CLOUDFLARED_EXE%" tunnel --no-autoupdate --url "%LOCAL_URL%"

echo.
echo Public access stopped.
pause
