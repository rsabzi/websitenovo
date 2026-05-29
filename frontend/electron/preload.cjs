const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('desktop', {
  selectFolder: () => ipcRenderer.invoke('select-folder'),
});
