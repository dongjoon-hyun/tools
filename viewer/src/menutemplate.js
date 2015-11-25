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
