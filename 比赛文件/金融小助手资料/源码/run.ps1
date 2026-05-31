$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$embeddedPython = Join-Path $root '.python\python.exe'
$server = Join-Path $root 'server.py'

if (Test-Path $embeddedPython) {
  $python = $embeddedPython
} else {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
  if (-not $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
  }
  if (-not $pythonCommand) {
    Write-Host 'Python was not found. Put portable Python at .python\python.exe or install Python 3.12+.' -ForegroundColor Yellow
    exit 1
  }
  $python = $pythonCommand.Source
}

Write-Host "Using Python: $python"
Write-Host 'Financial Assistant: http://127.0.0.1:18765'
Write-Host 'Press Ctrl+C to stop.'
& "$python" "$server"
