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
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.head.py 2> /dev/null'
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
	cmd = 'HADOOP_CONF_DIR=/etc/hive/conf /opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.sql.py 2> /dev/null'
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
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.count_line.py 2> /dev/null'
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
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.count_line_with.py 2> /dev/null'
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
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.grep.py 2> /dev/null'
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
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.select.py 2> /dev/null'
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
        .map(lambda line: line.replace(u"'"," ").replace(u"’"," ").replace(u"“"," ").replace(u"”"," ").replace(u"△"," ").replace(u"◇"," ")) \
        .flatMap(lambda line: regex.split(line)) \
        .filter(lambda word: len(word.strip())>0) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a,b: a+b) \
        .map(lambda (a,b): (b,a)) \
        .sortByKey(0,1) \
        .map(lambda (a,b): '%%s%%c%%s' %% (b,1,a))
counts.saveAsTextFile('%(outpath)s')
EOF''' % locals())
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.tf_ko.py 2> /dev/null'
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
	cmd = '/opt/spark/bin/spark-submit --num-executors 300 /home/hadoop/demo/spark.ngram_ko.py 2> /dev/null'
	run(cmd)


@task
def doc2sent(inpath, outpath):
    '''
    fab spark.doc2sent:/user/hadoop/demo/nlp/hani-doc,/user/hadoop/demo/nlp/hani-sent
    '''
    run('''cat <<EOF > /home/hadoop/demo/spark.doc2sent.py
# -*- encoding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.conf import SparkConf
import sys

inputFileName = '%(inpath)s'
outputFileName = '%(outpath)s'
print sys.argv

conf = SparkConf()
conf.setAppName('doc2sent')
sc = SparkContext(conf=conf)

docs = sc.textFile(inputFileName)
numDocs = docs.count()
sents = docs.flatMap(lambda line: line.split('.'))
numSents = sents.count()
sents.saveAsTextFile(outputFileName)
for s in sents.take(5):
    print s.encode('utf-8')
print 'Documents: ' + str(numDocs) + ' -> Sentences: ' + str(numSents)
print 'Completed: ' + outputFileName
EOF''' % locals())

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 /home/hadoop/demo/spark.doc2sent.py 2> /dev/null'
    run(cmd)


@task
def sent2kma(inpath, outpath, numpartitions, numthreads):
    '''
    fab spark.sent2kma:/user/hadoop/demo/nlp/1000_news_sample.txt,/user/hadoop/demo/nlp/1000_news_sample_kma.txt,20,4
    '''

    run('''cat <<EOF > /home/hadoop/demo/spark.sent2kma.py
# -*- encoding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.conf import SparkConf
import sys


nlpModuleName = 'kma'
inputFileName = '%(inpath)s'
outputFileName = '%(outpath)s'
numPartitions = int('%(numpartitions)s')
numThreads = int('%(numthreads)s')
print sys.argv

conf = SparkConf()
conf.setAppName('sent2kma')
sc = SparkContext(conf=conf)

scNLPModuleName = sc.broadcast(nlpModuleName)
scNumThreads = sc.broadcast(numThreads)

sents = sc.textFile(inputFileName)
if numPartitions >= 1 and numPartitions <= 30:
    print 'Repartition: ' + str(numPartitions)
    sents = sents.repartition(numPartitions)

def runKMA(pindex, lines):
    import sys
    sys.path.append('/hdfs/user/hadoop/javisnlp/')
    from JavisNLP import JavisNLP
    nlp = JavisNLP()
    nlp.init('/hdfs/user/hadoop/javisnlp/config/NLU.cfg')
    new_lines = nlp.runBatch(list(lines), scNumThreads.value, scNLPModuleName.value)
    return new_lines


results = sents.mapPartitionsWithIndex(runKMA)
results.saveAsTextFile(outputFileName)
for s in results.take(5):
    print s.encode('utf-8')
print 'Completed: ' + outputFileName
EOF''' % locals())

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G  --conf spark.executor.extraLibraryPath=/hdfs/user/hadoop/javisnlp/ /home/hadoop/demo/spark.sent2kma.py 2> /dev/null'
    run(cmd)


@task
def sent2ner(inpath, outpath, numpartitions, numthreads):
    '''
    fab spark.sent2ner:/user/hadoop/demo/nlp/1000_news_sample.txt,/user/hadoop/demo/nlp/1000_news_sample_ner.txt,20,4
    '''

    run('''cat <<EOF > /home/hadoop/demo/spark.sent2ner.py
# -*- encoding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.conf import SparkConf
import sys


nlpModuleName = 'ner'
inputFileName = '%(inpath)s'
outputFileName = '%(outpath)s'
numPartitions = int('%(numpartitions)s')
numThreads = int('%(numthreads)s')
print sys.argv

conf = SparkConf()
conf.setAppName('sent2ner')
sc = SparkContext(conf=conf)

scNLPModuleName = sc.broadcast(nlpModuleName)
scNumThreads = sc.broadcast(numThreads)

sents = sc.textFile(inputFileName)
if numPartitions >= 1 and numPartitions <= 30:
    print 'Repartition: ' + str(numPartitions)
    sents = sents.repartition(numPartitions)

def runNER(pindex, lines):
    import sys
    sys.path.append('/hdfs/user/hadoop/javisnlp/')
    from JavisNLP import JavisNLP
    nlp = JavisNLP()
    nlp.init('/hdfs/user/hadoop/javisnlp/config/NLU.cfg')
    new_lines = nlp.runBatch(list(lines), scNumThreads.value, scNLPModuleName.value)
    return new_lines


results = sents.mapPartitionsWithIndex(runNER)
results.saveAsTextFile(outputFileName)
for s in results.take(5):
    print s.encode('utf-8')
print 'Completed: ' + outputFileName
EOF''' % locals())

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G  --conf spark.executor.extraLibraryPath=/hdfs/user/hadoop/javisnlp/ /home/hadoop/demo/spark.sent2ner.py 2> /dev/null'
    run(cmd)


@task
def word2vec(inpath, queryword):
    '''
    fab spark.word2vec:/user/hadoop/demo/nlp/1000_news_sample_kma.txt,대통령
    '''
    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 /hdfs/user/hadoop/demo/nlp/SparkWord2Vec.py %(inpath)s %(queryword)s 2> /dev/null' % locals()
    run(cmd)
