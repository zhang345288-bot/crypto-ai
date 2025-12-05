# start_frontend.ps1
# Starts a simple static HTTP server for the frontend (port 3000)
Set-Location $PSScriptRoot
Write-Host "Starting frontend static server at http://localhost:3000 (serving from $PSScriptRoot)"
python -m http.server 3000
