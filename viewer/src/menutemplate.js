/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
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
          }
        },
        {
          label: 'View License',
          enabled: true,
          click: function () {
          }
        },
        {
          label: 'Version ' + app.getVersion(),
          enabled: false,
          click: function () {
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
          }
        },
        {
          type: 'separator'
        },
        {
          label: 'Hide Viewer',
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
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Developer',
          enabled: true,
          submenu: [
            {
              label: 'Toggle Developer Tools',
              enabled: true,
              accelerator: commandOrCtrl() + '+Alt+I',
              click: function() {
                require('electron').ipcRenderer.send('toggleDevTools', '');
              }
            }
          ]
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Show Licenses',
          enabled: true,
          click: function() {
            openLicense();
          }
        },
        {
          label: 'Send a feedback',
          enabled: true,
          click: function() {
            var newline = '%0A';
            var mailto = 'support@sfbasoft.com';
            var subject = '[v' + app.getVersion() + '/' + navigator.platform + '/' + navigator.language + '] Viewer Feedback';
            var comment = '[Feedback]' + newline + 'Please enter here' + newline.repeat(10);
            var version = '[Environment]' + newline;
            for (var prop in process.versions) {
              version += prop + ': v' + process.versions[prop] + newline;
            }
            var body = comment + version + newline;
            require('shell').openExternal('mailto:' + mailto + '?subject=' + subject + '\&body=' + body);
          }
        }
      ]
    }
  ]
};

module.exports = menuTemplate;
