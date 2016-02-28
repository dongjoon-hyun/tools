[![License](https://img.shields.io/badge/license-Apache%202-blue.svg)](LICENSE)

# Remote Shell via Telegram Bot

Very dangerous shell via Telegram.

### Make your bot.
  https://core.telegram.org/bots

### Set `.netrc` with Telegram Bot Token.
```
machine api.telegram.org
  login anonymous
  password <YOUR_TOKEN>
```

### Run
```
python telegram-shell.py
```

### Make your command script in `cmd` folder, e.g., `ls.sh`.
```
#!/bin/bash
ls repos
```

### Send `ls` to your bot and get the result.

