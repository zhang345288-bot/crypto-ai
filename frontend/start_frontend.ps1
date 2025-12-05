# start_frontend.ps1
# Starts a simple static HTTP server for the frontend (port 3000)
Set-Location $PSScriptRoot
Write-Host "Starting frontend static server at http://localhost:3000 (serving from $PSScriptRoot)"
Write-Host "Listing frontend directory contents for diagnostics:"
Get-ChildItem -Path $PSScriptRoot -Force | Select-Object Name,Mode,Length | ForEach-Object { Write-Host $_ }

$imagesPath = Join-Path $PSScriptRoot 'images'
if (Test-Path $imagesPath) {
	Write-Host "Found images directory. Listing up to 50 files:"
	Get-ChildItem -Path $imagesPath -File | Select-Object -First 50 Name | ForEach-Object { Write-Host " - " $_.Name }
} else {
	Write-Host "Images directory not found at: $imagesPath"
}

Write-Host "Starting http.server (serving from $PSScriptRoot)"
# Use --directory explicitly to avoid issues with working directory
python -m http.server 3000 --directory "$PSScriptRoot"
