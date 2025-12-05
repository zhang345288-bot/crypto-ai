# start_backend.ps1
# This script runs inside the backend folder window. Behavior:
# - If a bundled executable `crypto_ai_backend.exe` exists in `backend/`, run it.
# - Else if project `.venv` exists (in parent folder), activate it and run `python run_backend.py`.
# - Else show instructions to run `setup.ps1` or create a venv.

$scriptDir = $PSScriptRoot
$root = Split-Path $scriptDir -Parent
Set-Location $scriptDir

$exe = Join-Path $scriptDir 'crypto_ai_backend.exe'
$venvActivate = Join-Path $root '.venv\Scripts\Activate.ps1'

if (Test-Path $exe) {
    Write-Host "Found bundled backend executable. Starting..."
    & $exe
    exit
}

if (-not (Test-Path $venvActivate)) {
    Write-Host ".venv not found. Attempting to create and install dependencies (this may take a few minutes)..."
    $setup = Join-Path $root 'setup.ps1'
    if (Test-Path $setup) {
        Write-Host "Running project setup: $setup"
        # run setup.ps1 in project root to create .venv and install requirements
        # Use Bypass to avoid ExecutionPolicy preventing unsigned scripts when launched by double-click
        powershell -NoProfile -ExecutionPolicy Bypass -File $setup
    } else {
        Write-Host "setup.ps1 not found in project root. Please run setup.ps1 manually or follow README instructions."
        Pause
        exit
    }
}

if (Test-Path $venvActivate) {
    Write-Host "Activating .venv and starting backend..."
    . $venvActivate
    Set-Location $scriptDir
    python run_backend.py
} else {
    Write-Host "Failed to prepare .venv. Please check setup output and install dependencies manually."
    Pause
}
