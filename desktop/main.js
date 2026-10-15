/**
 * Electron shell: starts bundled FastAPI backend, then loads the SPA from the same origin.
 */

const { app, BrowserWindow } = require('electron')
const path = require('path')
const fs = require('fs')
const { spawn } = require('child_process')
const http = require('http')
const net = require('net')

/** @type {import('child_process').ChildProcess | null} */
let backendProc = null
/** @type {BrowserWindow | null} */
let mainWindow = null

function pickPort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer()
    srv.on('error', reject)
    srv.listen(0, '127.0.0.1', () => {
      const addr = srv.address()
      const p = typeof addr === 'object' && addr ? addr.port : 17890
      srv.close(() => resolve(p))
    })
  })
}

function waitForHealth(port, timeoutMs = 120000) {
  const deadline = Date.now() + timeoutMs
  return new Promise((resolve, reject) => {
    function attempt() {
      if (Date.now() > deadline) {
        reject(new Error('Backend did not respond on /health in time'))
        return
      }
      const req = http.get(`http://127.0.0.1:${port}/health`, (res) => {
        res.resume()
        if (res.statusCode === 200) {
          resolve()
        } else {
          setTimeout(attempt, 400)
        }
      })
      req.on('error', () => {
        setTimeout(attempt, 400)
      })
      req.setTimeout(2500, () => {
        req.destroy()
        setTimeout(attempt, 400)
      })
    }
    attempt()
  })
}

function backendCommand(port, userData) {
  const seedPackaged = path.join(process.resourcesPath, 'erm_seed.db')
  const seedDev = path.join(__dirname, 'resources', 'erm_seed.db')
  const seedDb = fs.existsSync(seedPackaged) ? seedPackaged : fs.existsSync(seedDev) ? seedDev : ''

  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
    ERM_SEED_DB: seedDb,
  }

  if (app.isPackaged) {
    const exe = path.join(process.resourcesPath, 'backend', 'erm-backend.exe')
    return { cmd: exe, args: ['--port', String(port), '--data-dir', userData], env }
  }

  const py = process.env.PYTHON || 'python'
  const script = path.join(__dirname, '..', 'BACK', 'run_desktop.py')
  return { cmd: py, args: [script, '--port', String(port), '--data-dir', userData], env }
}

async function startBackend(port) {
  const userData = app.getPath('userData')
  const { cmd, args, env } = backendCommand(port, userData)
  if (!fs.existsSync(cmd) && app.isPackaged) {
    throw new Error(`Backend executable not found: ${cmd}`)
  }
  backendProc = spawn(cmd, args, {
    env,
    cwd: app.isPackaged ? path.dirname(cmd) : path.join(__dirname, '..', 'BACK'),
    stdio: app.isPackaged ? 'ignore' : 'inherit',
  })
  backendProc.on('error', (err) => {
    console.error('Backend spawn error:', err)
  })
  backendProc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.error('Backend exited with code', code)
    }
  })
}

function killBackend() {
  if (!backendProc || backendProc.killed) return
  try {
    if (process.platform === 'win32' && backendProc.pid) {
      const { execSync } = require('child_process')
      execSync(`taskkill /PID ${backendProc.pid} /T /F`, { stdio: 'ignore' })
    } else {
      backendProc.kill('SIGTERM')
    }
  } catch {
    try {
      backendProc.kill('SIGKILL')
    } catch {
      /* ignore */
    }
  }
  backendProc = null
}

async function createWindow() {
  const port = await pickPort()
  await startBackend(port)
  await waitForHealth(port)

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  await mainWindow.loadURL(`http://127.0.0.1:${port}/`)
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(async () => {
  try {
    await createWindow()
  } catch (e) {
    console.error(e)
    const { dialog } = require('electron')
    dialog.showErrorBox(
      'ERM Prototype failed to start',
      String(e && e.message ? e.message : e) +
        '\n\nIf you are in development mode, run the API from BACK with Python, or build the backend first.',
    )
    app.quit()
  }
})

app.on('window-all-closed', () => {
  killBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  killBackend()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow().catch(console.error)
  }
})
