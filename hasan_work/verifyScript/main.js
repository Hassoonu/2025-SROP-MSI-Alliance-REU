
const {app, BrowserWindow, ipcMain } = require('electron/main')
const exec = require('child_process')


const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 400
    })   

    win.loadFile("index.html")
}

app.whenReady().then(() => {
    createWindow()

    app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) createWindow()
                // this specific function is due to macs, since after closign they remain open.
                // if user wants to re-open, then this allows the application to start another window
                // if user re-clicks program to activate.
        })
})

app.on("window-all-closed", () => {
    if(process.platform !== 'darwin'){
        app.quit()
    }
})


ipcMain.handle('next-dataset', () => {
  return execPromise('python visualize.py --action=next');
});

ipcMain.handle('prev-dataset', () => {
  return execPromise('python visualize.py --action=prev');
});

ipcMain.handle('delete-dataset', () => {
  return execPromise('python visualize.py --action=delete');
});

ipcMain.handle('accept-dataset', () => {
  return execPromise('python visualize.py --action=delete');
});

// Helper
function execPromise(command) {
  return new Promise((resolve, reject) => {
    exec(command, (err, stdout, stderr) => {
      if (err) reject(stderr);
      else resolve(stdout);
    });
  });
}