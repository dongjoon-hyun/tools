var app = require('app');
var BrowserWindow = require('browser-window');
const ipcMain = require('electron').ipcMain;

var win = null;

var shouldQuit = app.makeSingleInstance(function(commandLine, workingDirectory) {
  if (win) {
    if (win.isMinimized()) {
      win.restore();
    }
    win.focus();
  }
  return true;
});

if (shouldQuit) {
  app.quit();
  return;
}

app.on('will-finish-launching', function() {
  require('crash-reporter').start({
    productName: 'Viewer',
    companyName: 'SFBASoft, Inc',
    submitURL: 'https://sfbasoft.com/post',
    autoSubmit: true
  });

  // TODO: Auto Updater
});

app.on('window-all-closed', function() {
  app.quit();
});

app.on('ready', function() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    frame: process.platform === 'win32',
    transparent: true
  });
  win.loadURL('file://' + __dirname + '/index.html');
  win.on('closed', function() {
    win = null;
  });
  win.webContents.openDevTools();
});

ipcMain.on('openDevTools', function(event, arg) {
  win.webContents.openDevTools();
});

ipcMain.on('closeDevTools', function(event, arg) {
  win.webContents.closeDevTools();
});
