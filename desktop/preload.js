const { contextBridge } = require('electron')

contextBridge.exposeInMainWorld('ermDesktop', {
  isDesktop: true,
})
