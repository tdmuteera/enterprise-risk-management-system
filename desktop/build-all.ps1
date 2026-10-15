# Build Windows installer: frontend -> seed DB -> PyInstaller backend -> electron-builder NSIS
# Run from repository root (VANA DUMI) or from desktop folder.
$ErrorActionPreference = "Stop"
$Desktop = $PSScriptRoot
$Root = Split-Path -Parent $Desktop
$Back = Join-Path $Root "BACK"
$Front = Join-Path $Root "FRONT"
$venvPy = Join-Path $Back ".venv\Scripts\python.exe"
$venvPip = Join-Path $Back ".venv\Scripts\pip.exe"
$venvPyi = Join-Path $Back ".venv\Scripts\pyinstaller.exe"
if (-not (Test-Path $venvPy)) {
  Write-Error "BACK\.venv not found. Create venv in BACK and pip install -r requirements.txt"
}

Write-Host "== 1/4 Frontend (desktop mode: relative API) ==" -ForegroundColor Cyan
Push-Location $Front
npm install
npm run build:desktop
Pop-Location

$spaOut = Join-Path $Desktop "resources\spa"
if (Test-Path $spaOut) { Remove-Item -Recurse -Force $spaOut }
New-Item -ItemType Directory -Path $spaOut -Force | Out-Null
Copy-Item -Path (Join-Path $Front "dist\*") -Destination $spaOut -Recurse -Force

Write-Host "== 2/4 Seeded SQLite (erm_seed.db) ==" -ForegroundColor Cyan
Push-Location $Back
& $venvPy "build_desktop_seed.py"
Pop-Location

Write-Host "== 3/4 PyInstaller backend ==" -ForegroundColor Cyan
& $venvPip install pyinstaller -q
Push-Location $Desktop
& $venvPyi --noconfirm erm-backend.spec
Pop-Location

Write-Host "== 4/4 Electron NSIS installer ==" -ForegroundColor Cyan
Push-Location $Desktop
npm install
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
npm run dist
Pop-Location

Write-Host "Done. Installer under: $Desktop\release\" -ForegroundColor Green
