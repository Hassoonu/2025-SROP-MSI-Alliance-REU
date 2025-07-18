<<<<<<< HEAD
const { ipcRenderer, contextBridge } = require('electron')


contextBridge.exposeInMainWorld("dataAPI", {
    action: (action) => ipcRenderer.invoke(`${action}-dataset`),
});
=======
// const { ipcRenderer, contextBridge } = require('electron')


// contextBridge.exposeInMainWorld("dataAPI", {
//     action: (action) => ipcRenderer.invoke(`${action}-dataset`),
// });
>>>>>>> verifyScript
