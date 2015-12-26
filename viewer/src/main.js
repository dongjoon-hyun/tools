/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
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
    frame: true,
    transparent: false
  });
  win.loadURL('file://' + __dirname + '/index.html');
  win.on('closed', function() {
    win = null;
  });
});

ipcMain.on('openDevTools', function(event, arg) {
  win.webContents.openDevTools();
});

ipcMain.on('closeDevTools', function(event, arg) {
  win.webContents.closeDevTools();
});
