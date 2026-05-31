@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.python\python.exe"
set "SERVER=%~dp0server.py"

if exist "%PYTHON_EXE%" (
  set "PY=%PYTHON_EXE%"
  echo Using portable Python...
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PY=python"
    echo Using system Python...
  ) else (
    where py >nul 2>nul
    if not errorlevel 1 (
      set "PY=py"
      echo Using Python launcher...
    ) else (
      echo Python was not found.
      echo Put portable Python at .python\python.exe or install Python 3.12+.
      pause
      exit /b 1
    )
  )
)

echo Financial Assistant: http://127.0.0.1:18765
echo Press Ctrl+C to stop.
"%PY%" "%SERVER%"
pause
