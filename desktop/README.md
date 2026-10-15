# ERM Prototype — Desktop (Electron + FastAPI + SQLite)

This folder packages the **React frontend** and **FastAPI backend** into a **Windows desktop app** with a **pre-seeded SQLite database**. End users install via the generated **NSIS setup** and run everything **locally** (no separate Postgres install).

## What gets installed

| Component | Role |
|-----------|------|
| **Electron** | Window + lifecycle; starts/stops the API |
| **erm-backend.exe** (PyInstaller) | Uvicorn + FastAPI on `127.0.0.1` + random free port |
| **spa** (Vite `dist`) | Served by FastAPI at `/` (same origin as `/api/v1`) |
| **erm_seed.db** | Copied once to `%APPDATA%\ERM Prototype\erm.db` on first launch |

## Prerequisites (build machine)

- Node.js 18+ and npm  
- Python **BACK** virtualenv at `BACK\.venv` with `pip install -r requirements.txt`  
- Windows (for `.exe` / NSIS; macOS/Linux would need different `electron-builder` targets)

## One-shot build (recommended)

From **PowerShell**, in this folder:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build-all.ps1
```

Output: **`release\ERM-Prototype-Setup-1.0.0.exe`** (name follows `package.json` version). To ship as a literal `Setup.exe`, rename the file or change `build.win.artifactName` in `package.json`.

Windows code signing is **turned off** in this repo (`signAndEditExecutable: false` and `CSC_IDENTITY_AUTO_DISCOVERY=false` in `build-all.ps1`) so the build works without Developer Mode / symlink privileges. For production, add a certificate and signing configuration.

## Run without installer (dev)

1. Build frontend and copy SPA (or run full `build-all.ps1` once).  
2. From **BACK** folder:

   ```powershell
   $env:ERM_SEED_DB = "..\desktop\resources\erm_seed.db"
   python run_desktop.py --port 17890 --data-dir "$env:TEMP\erm-desktop-test"
   ```

3. From **desktop** folder: `npm start` (Electron starts its own backend if you prefer, point is same).

Or only Electron after PyInstaller:

```powershell
cd desktop
npm install
npm start
```

(Packaged layout: `dist\erm-backend\` must exist and `resources\erm_seed.db`.)

## Demo logins

From `db_seed.py` (same data as `erm_seed.db`):

| Email | Password |
|-------|----------|
| admin@erm.edu | AdminPass123! |
| risk.officer@erm.edu | RiskOff123! |
| executive@erm.edu | ExecPass123! |

(Other seeded users: `FinUser123!`, `HRUser123!`, `AcadUser123!`, etc.)

## Security note

This is a **prototype**: a fixed `SECRET_KEY` is used for the desktop bundle. Do **not** use this installer as a production deployment without hardening (secrets, HTTPS, code signing, updates).

## Files

- `main.js` — spawns backend, waits for `/health`, opens `http://127.0.0.1:<port>/`  
- `erm-backend.spec` — PyInstaller onedir bundle  
- `resources/erm_seed.db` — built by `BACK\build_desktop_seed.py`  
- `resources/spa/` — copy of `FRONT\dist` at pack time  

## Troubleshooting

- **Blank window**: wait a few seconds; backend cold-start can be slow. Check `%TEMP%` or run `erm-backend.exe` from a console to see logs.  
- **Antivirus**: PyInstaller bundles are sometimes flagged; you may need an exception or code signing.  
- **Port in use**: Electron picks a random free port each run.
