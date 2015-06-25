#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
'''
Intelligence Platform CLI Fabric File
'''

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.2'

from fabric.api import *

@task
def head(inpath, count=5):
	'''
	fab spark.head:/data/image/imagenet/*.txt,5
	'''
	run('''cat <<EOF > /home/hadoop/demo/spark.head.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Head')
for x in sc.textFile('%(inpath)s').take(%(count)s):
	print x.encode('utf8')
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.head.py 2> /dev/null'
	run(cmd)

@task
def sql(sql):
	'''
	fab spark.sql:'select count(*) from data.news'
	'''
	run('''cat <<EOF > /home/hadoop/demo/spark.sql.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import HiveContext
sc = SparkContext(appName='HiveContext')
sqlContext = HiveContext(sc)
for x in sqlContext.sql('%(sql)s').collect():
	print x
EOF''' % locals())
	cmd = 'HADOOP_CONF_DIR=/etc/hive/conf /usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.sql.py 2> /dev/null'
	run(cmd)

@task
def count_line(inpath):
	'''
	fab spark.count_line:/data/image/imagenet/*.txt
	'''
	run('''cat <<EOF > /home/hadoop/demo/spark.count_line.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Count Line')
print sc.textFile('%(inpath)s').count()
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.count_line.py 2> /dev/null'
	run(cmd)

@task
def count_line_with(inpath, keyword):
	'''
	fab spark.count_line_with:/data/text/wikipedia/ko*,'<page>'
	'''
	run('''cat <<EOF > /home/hadoop/demo/spark.count_line_with.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Grep')
print sc.textFile('%(inpath)s').filter(lambda line: '%(keyword)s' in line).count()
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.count_line_with.py 2> /dev/null'
	run(cmd)

@task
def grep(inpath, outpath, keyword):
	'''
	fab spark.grep:/data/text/wikipedia/ko*,/user/hadoop/grep_result,'<page>'
	'''
	run('''cat <<EOF > /home/hadoop/demo/spark.grep.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Grep')
sc.textFile('%(inpath)s').filter(lambda line: '%(keyword)s' in line).saveAsTextFile('%(outpath)s')
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.grep.py 2> /dev/null'
	run(cmd)

@task
def select(inpath, outpath, columns='*', sep='\01'):
	'''
	fab spark.select:/data/text/news/hani/*,/user/hadoop/selected,'1;0'
	'''
	run('''cat <<EOF > /home/hadoop/demo/spark.select.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
import re
sc = SparkContext(appName='Select')
columns = '%(columns)s'
def select(alist, cols):
	blist = [alist[c] for c in cols]
	return ('%%c' %% (1)).join(blist)
if '*' == columns:
	cols = xrange(len(columns.split(';')))
else:
	cols = [int(i) for i in columns.split(';')]
sc.textFile('%(inpath)s').map(lambda line: select(re.split('%%c' %% (1),line), cols)).saveAsTextFile('%(outpath)s')
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.select.py 2> /dev/null'
	run(cmd)

@task
def tf_ko(inpath,outpath,sep='\01'):
	'''
	fab spark.tf_ko:/data/text/news/hani/*,/user/hadoop/tf_result
	'''
	if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
		print 'Unauthorized path: %(outpath)s' % locals()
		return
	run('''cat <<EOF > /home/hadoop/demo/spark.tf_ko.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
import re
import string
regex = re.compile(r'[%%s\s0-9a-zA-Z~·]+' %% re.escape(string.punctuation))
sc = SparkContext(appName='Term Frequency')
counts = sc.textFile('%(inpath)s') \
        .map(lambda line: re.split('%%c' %% (1),line)[1]) \
        .map(lambda line: line.replace(u"‘"," ").replace(u"’"," ").replace(u"“"," ").replace(u"”"," ").replace(u"△"," ").replace(u"◇"," ")) \
        .flatMap(lambda line: regex.split(line)) \
        .filter(lambda word: len(word.strip())>0) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a,b: a+b) \
        .map(lambda (a,b): (b,a)) \
        .sortByKey(0,1) \
        .map(lambda (a,b): '%%s%%c%%s' %% (b,1,a))
counts.saveAsTextFile('%(outpath)s')
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.tf_ko.py 2> /dev/null'
	run(cmd)

@task
def ngram_ko(n,min,inpath,outpath,sep='\01'):
	'''
	fab spark.ngram_ko:2,1000,/user/hadoop/tf_result,/user/hadoop/ngram_result
	'''
	if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
		print 'Unauthorized path: %(outpath)s' % locals()
		return
	run('''cat <<EOF > /home/hadoop/demo/spark.ngram_ko.py
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
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.ngram_ko.py 2> /dev/null'
	run(cmd)

@task
def sent2kma(inpath, outpath, numpartitions):
    '''
    fab spark.sent2kma:/user/hadoop/demo/nlp/1000_news_sample.txt,/user/hadoop/demo/nlp/1000_news_sample_kma.txt,20
    '''
    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 /hdfs/user/hadoop/demo/nlp/SparkJavisNLP.py %(inpath)s %(outpath)s, %(numpartitions)s 2> /dev/null' % locals()
    run(cmd)


@task
def word2vec(inpath, queryword):
    '''
    fab spark.word2vec:/user/hadoop/demo/nlp/1000_news_sample_kma.txt,대통령
    '''
    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 /hdfs/user/hadoop/demo/nlp/SparkWord2Vec.py %(inpath)s %(queryword)s 2> /dev/null' % locals()
    run(cmd)
