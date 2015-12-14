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
var commandOrCtrl = function () {
  return process.platform != 'darwin' ? 'Ctrl' : 'Command';
};

var menuTemplate = function () {
  return [
    {
      label: 'Viewer',
      submenu: [
        {
          label: 'About Viewer',
          enabled: true,
          click: function () {
            //router.get().transitionTo('about');
          }
        },
        {
          type: 'separator'
        },
        {
          label: 'Preferences',
          accelerator: commandOrCtrl() + '+,',
          enabled: true,
          click: function () {
            //router.get().transitionTo('preferences');
          }
        },
        {
          type: 'separator'
        },
        {
          type: 'separator'
        },
        {
          label: 'Hide',
          accelerator: commandOrCtrl() + '+H',
          selector: 'hide:'
        },
        {
          label: 'Hide Others',
          accelerator: commandOrCtrl() + '+Shift+H',
          selector: 'hideOtherApplications:'
        },
        {
          label: 'Show All',
          selector: 'unhideAllApplications:'
        },
        {
          label: 'Show Debug',
          accelerator: commandOrCtrl() + '+d',
          click: function() {
            require('electron').ipcRenderer.send('openDevTools', '');
          }
        },
        {
          label: 'Hide Debug',
          click: function() {
            require('electron').ipcRenderer.send('closeDevTools', '');
          }
        },
        {
          type: 'separator'
        },
        {
          label: 'Quit',
          accelerator: commandOrCtrl() + '+Q',
          click: function() {
            require('electron').remote.require('app').quit();
          }
        }
      ]
    },
    {
      label: 'Cluster',
      submenu: [
        {
          label: 'Add',
          accelerator: commandOrCtrl() + '+A',
          enabled: true,
          click: function () {
          }
        },
        {
          type: 'separator'
        },
      ]
    }
  ]
};

module.exports = menuTemplate;
