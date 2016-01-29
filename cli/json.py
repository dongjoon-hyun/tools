#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
JSON CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import task, run, env, cd


@task
def schema(inpath):
    """
    fab json.schema:/data/text/twitter
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > json.schema.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext(appName='JSON Schema')
sqlContext = SQLContext(sc)
df = sqlContext.read.json('%(inpath)s')
df.printSchema()
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit json.schema.py 2> /dev/null'
        run(cmd)


@task
def filter(inpath, field, value, outpath):
    """
    fab json.filter:/data/text/twitter/20150721_22.json,lang,ko,/tmp/ko
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > json.filter.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext(appName='JSON Filter')
sqlContext = SQLContext(sc)
df = sqlContext.read.json('%(inpath)s')
df.filter(df['%(field)s']=='%(value)s').write.save('%(outpath)s', format='json')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit json.filter.py 2> /dev/null'
        run(cmd)


@task
def select(inpath, columns, outpath):
    """
    fab json.select:/data/text/twitter/20150721_22.json,created_at:text,/tmp/result
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        columns = ','.join(map(lambda x: "'%s'" % x, columns.split(':')))
        run('''cat <<EOF > json.select.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext(appName='JSON Select')
sqlContext = SQLContext(sc)
df = sqlContext.read.json('%(inpath)s')
df.select(%(columns)s).write.save('%(outpath)s', format='json')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit json.select.py 2> /dev/null'
        run(cmd)
