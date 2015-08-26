#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'

from fabric.api import *


@task
def sql(sql='show tables'):
    """
    fab hive.sql:'select count(*) from data.news'
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > sql.hive
%(sql)s
EOF''' % locals())
        cmd = '/usr/bin/hive -S --hiveconf mapred.map.tasks=300 --hiveconf hive.merge.mapfiles=false -f sql.hive 2> /dev/null'
        run(cmd)
