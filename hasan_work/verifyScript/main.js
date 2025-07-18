
const {app, BrowserWindow, ipcMain } = require('electron/main')
<<<<<<< HEAD
const exec = require('child_process')
=======
const { spawn } = require('child_process')

const pythonProcess = spawn('python', ['visualize.py']);

pythonProcess.stdout.on('data', (data) => {
  console.log(`PYTHON: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
  console.error(`PYTHON ERROR: ${data}`);
});

pythonProcess.on('close', (code) => {
  console.log(`Python process exited with code ${code}`);
});


>>>>>>> verifyScript


const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
<<<<<<< HEAD
        height: 400
=======
        height: 600,
        resizable: true
>>>>>>> verifyScript
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


<<<<<<< HEAD
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
=======
// ipcMain.handle('next-dataset', () => {
//   return execPromise('python visualize.py --action=next');
// });

// ipcMain.handle('prev-dataset', () => {
//   return execPromise('python visualize.py --action=prev');
// });

// ipcMain.handle('delete-dataset', () => {
//   return execPromise('python visualize.py --action=delete');
// });

// ipcMain.handle('accept-dataset', () => {
//   return execPromise('python visualize.py --action=delete');
// });

// Helper
// function execPromise(command) {
//   return new Promise((resolve, reject) => {
//     exec(command, (err, stdout, stderr) => {
//       if (err) reject(stderr);
//       else resolve(stdout);
//     });
//   });
// }
>>>>>>> verifyScript
