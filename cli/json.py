#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

from fabric.api import *

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'


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
