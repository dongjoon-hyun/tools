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
@hosts('tip@54.64.24.132')
def send_message(id, msg):
    """
    fab tg.send_message:Soonwoong_Lee,'안녕하세요. 반갑습니다.'
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > tg_run.sh
#!/bin/bash
(echo "contact_list"; sleep 7; echo "msg %(id)s %(msg)s"; echo "safe_quit") | /home/tip/tg/bin/telegram-cli -k /home/tip/tg/tg-server.pub -W 2> /dev/null
EOF''' % locals())
        run('chmod +x ./tg_run.sh')
        cmd = './tg_run.sh > /dev/null 2>&1'
        run(cmd)