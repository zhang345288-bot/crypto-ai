# setup.ps1
# Creates a .venv in the project root and installs dependencies from requirements.txt
# Run this from the project root or let `backend\start_backend.ps1` call it automatically.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location $root

Write-Host "Project root: $root"

$venvPath = Join-Path $root '.venv'
$requirements = Join-Path $root 'requirements.txt'

try {
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtual environment at $venvPath..."
        python -m venv .venv
    } else {
        Write-Host ".venv already exists. Skipping creation."
    }

    Write-Host "Activating .venv..."
    . "$venvPath\Scripts\Activate.ps1"

    Write-Host "Upgrading pip..."
    python -m pip install --upgrade pip

    if (Test-Path $requirements) {
        Write-Host "Installing requirements from requirements.txt..."
        pip install -r $requirements
    } else {
        Write-Host "requirements.txt not found in project root. Please provide dependencies file."
    }

    Write-Host "Setup completed. You can now run:"
    Write-Host "  powershell -NoProfile -ExecutionPolicy RemoteSigned -File backend\\start_backend.ps1"
    Write-Host "Or double-click start.bat to launch both frontend and backend."
} catch {
    Write-Error "Setup failed: $_"
    Pause
    exit 1
}
