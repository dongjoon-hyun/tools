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
Spark CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import *


@task
def head(inpath, count=5):
    """
    fab spark.head:/data/image/imagenet/*.txt,5
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.head.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Head')
for x in sc.textFile('%(inpath)s').take(%(count)s):
    print x.encode('utf8')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.head.py 2> /dev/null'
        run(cmd)


@task
def sql(sql):
    """
    fab spark.sql:'select count(*) from data.news'
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.sql.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import HiveContext
sc = SparkContext(appName='HiveContext')
sqlContext = HiveContext(sc)
for x in sqlContext.sql('%(sql)s').collect():
    print x
EOF''' % locals())
        cmd = 'HADOOP_CONF_DIR=/etc/hive/conf /opt/spark/bin/spark-submit --num-executors 300 spark.sql.py 2> /dev/null'
        run(cmd)


@task
def count_line(inpath):
    """
    fab spark.count_line:/data/image/imagenet/*.txt
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.count_line.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Count Line')
print sc.textFile('%(inpath)s').count()
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.count_line.py 2> /dev/null'
        run(cmd)


@task
def count_line_with(inpath, keyword):
    """
    fab spark.count_line_with:/data/text/wikipedia/ko*,'<page>'
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.count_line_with.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Count Line With')
words = '%(keyword)s'.split(':')
def isIn(line):
    line = line.encode('utf8')
    for w in words:
        if w in line:
            return True
    return False
print sc.textFile('%(inpath)s').filter(isIn).count()
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.count_line_with.py 2> /dev/null'
        run(cmd)


@task
def grep(inpath, outpath, keyword):
    """
    fab spark.grep:/data/text/wikipedia/ko*,/user/hadoop/grep_result,'<page>'
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.grep.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Grep')
sc.textFile('%(inpath)s').filter(lambda line: '%(keyword)s' in line).saveAsTextFile('%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.grep.py 2> /dev/null'
        run(cmd)


@task
def select(inpath, outpath, columns='*', sep='\01'):
    """
    fab spark.select:/data/text/news/hani/*,/user/hadoop/selected,1:0
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.select.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
import re
sc = SparkContext(appName='Select')
columns = '%(columns)s'
def select(alist, cols):
    blist = [alist[c] for c in cols]
    return ('%%c' %% (1)).join(blist)
if '*' == columns:
    cols = xrange(len(columns.split(':')))
else:
    cols = [int(i) for i in columns.split(':')]
sc.textFile('%(inpath)s').map(lambda line: select(re.split('%%c' %% (1),line), cols)).saveAsTextFile('%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.select.py 2> /dev/null'
        run(cmd)


@task
def tf_ko(inpath, outpath, sep='\01'):
    """
    fab spark.tf_ko:/data/text/news/hani/*,/user/hadoop/tf_result
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.tf_ko.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
import re
import string

def normalize(str):
    chars = [u'N' if c.isdigit() else c for c in str]
    chars = [c for c in chars if c.isspace() or c == u'.' or c == u'N' or (44032 <= ord(c) and ord(c)<=55215)]
    return ''.join(chars)

sc = SparkContext(appName='Term Frequency')
counts = sc.textFile('%(inpath)s') \
    .map(lambda line: re.split('%%c' %% (1),line)[1]) \
    .map(normalize) \
    .flatMap(lambda line: regex.split(line)) \
    .filter(lambda word: len(word.strip())>0) \
    .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a,b: a+b) \
        .map(lambda (a,b): (b,a)) \
        .sortByKey(0,1) \
        .map(lambda (a,b): '%%s%%c%%s' %% (b,1,a))
counts.saveAsTextFile('%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.tf_ko.py 2> /dev/null'
        run(cmd)


@task
def ngram_ko(n, min, inpath, outpath, sep='\01'):
    """
    fab spark.ngram_ko:2,1000,/user/hadoop/tf_result,/user/hadoop/ngram_result
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.ngram_ko.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
import re
sc = SparkContext(appName='%(n)s-gram')
def ngram(line):
    n = %(n)s
        str = re.split('%%c' %% (1),line)[0]
        count = int(re.split('%%c' %% (1),line)[1])
        return [(str[i:i+n],count) for i in range(len(str)-n+1)]
counts = sc.textFile('%(inpath)s') \
        .flatMap(ngram) \
        .reduceByKey(lambda a,b: a+b) \
        .filter(lambda (a,b): b>=%(min)s) \
        .map(lambda (a,b): (b,a)) \
        .sortByKey(0,1) \
        .map(lambda (a,b): '%%s%%c%%s' %% (b,1,a))
counts.saveAsTextFile('%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.ngram_ko.py 2> /dev/null'
        run(cmd)


@task
def word2vec(inpath, queryword):
    """
    fab spark.word2vec:/sample/sample_hani_kma,대통령
    """
    cmd = '/opt/spark/bin/spark-submit /hdfs/user/hadoop/demo/nlp/SparkWord2Vec.py %(inpath)s %(queryword)s \
2> /dev/null' % locals()
    run(cmd)


@task
def naivebayes_train(inpath, lambda_, outpath):
    """
    fab spark.naivebayes_train:/sample/sample_naive_bayes_data.txt,1.0,/tmp/nb.model
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.naivebayes_train.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint

def parseLine(line):
    parts = line.split(',')
    label = float(parts[0])
    features = Vectors.dense([float(x) for x in parts[1].split(' ')])
    return LabeledPoint(label, features)

sc = SparkContext(appName='Naive Bayes Train')
data = sc.textFile('%(inpath)s').map(parseLine)
model = NaiveBayes.train(data, %(lambda_)s)
model.save(sc, '%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit spark.naivebayes_train.py 2> /dev/null'
        run(cmd)


@task
def naivebayes_predict(model, inpath, outpath):
    """
    fab spark.naivebayes_predict:/tmp/nb.model,/sample/naive_bayes_test.txt,/tmp/nb.result
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.naivebayes_test.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.mllib.classification import NaiveBayesModel
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint

def parseLine(line):
    features = Vectors.dense([float(x) for x in line.split(' ')])
    return features

sc = SparkContext(appName='Naive Bayes Predict')
model = NaiveBayesModel.load(sc, '%(model)s')
sc.textFile('%(inpath)s').map(parseLine).map(model.predict).saveAsTextFile('%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit spark.naivebayes_test.py 2> /dev/null'
        run(cmd)


@task
def sample(inpath, replacement, fraction, seed, outpath):
    """
    fab spark.sample:/sample/sample_movielens_movies.txt,False,0.5,0,/tmp/sampled_movielens
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > spark.sample.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Sampling')
sc.textFile('%(inpath)s').sample(%(replacement)s,%(fraction)s,%(seed)s).saveAsTextFile('%(outpath)s')
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit --num-executors 300 spark.sample.py 2> /dev/null'
        run(cmd)


@task
def lm(inpath, outpath, step, maxiter):
    """
    fab spark.lm:/sample/sample_regression,/user/hadoop/lm_result,0.1,1000
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > spark.lm.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.feature import StandardScaler
from pyspark.mllib.regression import LabeledPoint, LinearRegressionWithSGD
sc = SparkContext(appName='Linear Regression')

data = sc.textFile('%(inpath)s').filter(lambda x: not x.startswith('#')).map(lambda x: x.split())
label = data.map(lambda x: x[-1])
feature = data.map(lambda x: x[0:-1])
scaler = StandardScaler().fit(feature)
feature = scaler.transform(feature)
model = LinearRegressionWithSGD.train(label.zip(feature).map(lambda (x,y): LabeledPoint(x,y)), intercept=True, \
iterations=%(maxiter)s, step=%(step)s)
print model
EOF''' % locals())
        cmd = '/opt/spark/bin/spark-submit spark.lm.py 2> /dev/null'
        run(cmd)
