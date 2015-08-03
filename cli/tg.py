#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

__author__    = 'Soonwoong Lee (soonwoong.lee@gmail.com)'
__license__   = 'Apache License'
__version__   = '0.2'

from fabric.api import *

@task
def send_message(msg, id=-36901391):
    """
    fab tg.send_message:'안녕하세요. TIP Bot 입니다.'
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > tg_bot_request.py
# -*- coding: utf-8 -*-
import telegram
bot = telegram.Bot(token='112152357:AAGBdO_TGBagwQCsoGWm4EcZNv1CRwhJ0JA')
bot.sendMessage(chat_id=%(id)s, text='%(msg)s')
EOF''' % locals())
        cmd = 'python2.7 ./tg_bot_request.py 2>/dev/null'
        run(cmd)
        
@task
def send_photo(photo_path, id=-36901391):
    """
    fab tg.send_photo:https://telegram.org/img/t_logo.png
    """
    run('mkdir %s' % env.dir)
    photo_path = 'open("' + photo_path + '", "rb")' if 'http' not in photo_path else '"' + photo_path + '"'
    with cd(env.dir):
        run('''cat <<EOF > tg_bot_request.py
# -*- coding: utf-8 -*-
import telegram
bot = telegram.Bot(token='112152357:AAGBdO_TGBagwQCsoGWm4EcZNv1CRwhJ0JA')
bot.sendPhoto(chat_id=%(id)s, photo=%(photo_path)s)
EOF''' % locals())
        cmd = 'python2.7 ./tg_bot_request.py 2>/dev/null'
        run(cmd)
    