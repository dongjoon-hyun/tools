var app = require('app');
var BrowserWindow = require('browser-window');
const ipcMain = require('electron').ipcMain;

var mainWindow = null;

var shouldQuit = app.makeSingleInstance(function(commandLine, workingDirectory) {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
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
  mainWindow = new BrowserWindow({width: 1200, height: 800});
  mainWindow.loadURL('file://' + __dirname + '/index.html');
  mainWindow.on('closed', function() {
    mainWindow = null;
  });
  mainWindow.webContents.openDevTools();
});

ipcMain.on('openDevTools', function(event, arg) {
  mainWindow.webContents.openDevTools();
});

ipcMain.on('closeDevTools', function(event, arg) {
  mainWindow.webContents.closeDevTools();
});
