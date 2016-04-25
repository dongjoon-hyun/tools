#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import getpass
import netrc
import subprocess
import telebot

info = netrc.netrc()
login, account, password = info.authenticators("api.telegram.org")
token = password
bot = telebot.TeleBot(token)

def run(cmd, message):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out, err
    bot.send_message(message.chat.id, '```\n' + out + '```',
                     disable_web_page_preview=True,
                     disable_notification=True,
                     parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def shell(message):
    try:
        if message.from_user.username == getpass.getuser():
            cmd = message.text.split()
            cmd[0] = 'cmd/%s.sh' % cmd[0]
            print cmd
            run(cmd, message)
        else:
            print message.from_user.username, message.text
    except:
        print message

bot.polling()
