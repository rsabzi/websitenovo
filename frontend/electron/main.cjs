const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

const isDev = !app.isPackaged;

let backendProcess;

function startBackend() {
  const cwd = path.resolve(__dirname, '..', '..');
  backendProcess = spawn(process.env.PYTHON || 'python', ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8765'], {
    cwd,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });
}

function createWindow() {
  const window = new BrowserWindow({
    width: 1320,
    height: 860,
    minWidth: 1080,
    minHeight: 720,
    title: 'AI File Organizer',
    backgroundColor: '#020617',
    webPreferences: { preload: path.join(__dirname, 'preload.cjs') },
  });
  window.setMenuBarVisibility(false);
  const url = isDev ? 'http://127.0.0.1:5173' : `file://${path.join(__dirname, '../dist/index.html')}`;
  window.loadURL(url);
}

app.whenReady().then(() => {
  startBackend();
  ipcMain.handle('select-folder', async () => {
    const result = await dialog.showOpenDialog({ properties: ['openDirectory', 'multiSelections'] });
    return result.canceled ? [] : result.filePaths;
  });
  createWindow();
});

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});
