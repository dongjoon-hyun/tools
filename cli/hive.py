#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

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

"""
Hive CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import task, run, env, cd


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
        cmd = '/usr/bin/hive -S --hiveconf mapred.map.tasks=300 --hiveconf hive.merge.mapfiles=false -f sql.hive \
2> /dev/null'
        run(cmd)
