#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
'''
Intelligence Platform CLI Fabric File
'''

__author__    = 'Soonwoong Lee (soonwoong.lee@gmail.com)'
__license__   = 'Apache License'
__version__   = '0.2'

from fabric.api import *

@task
def doc2sent(inpath, outpath):
    '''
    fab nlp.doc2sent:/data/sample/sample_hani_doc,/user/hadoop/sample_hani_sent
    '''
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
	print 'Unauthorized path: %(outpath)s' % locals()
	return
    run('hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null' % locals())
    run('''cat <<EOF > /home/hadoop/demo/nlp.doc2sent.py
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

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 /home/hadoop/demo/nlp.doc2sent.py 2> /dev/null'
    run(cmd)


@task
def sent2kma(inpath, outpath, numpartitions, numthreads):
    '''
    fab nlp.sent2kma:/data/sample/sample_hani_sent,/user/hadoop/sample_hani_kma,20,4
    '''
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
	print 'Unauthorized path: %(outpath)s' % locals()
	return
    run('hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null' % locals())
    run('''cat <<EOF > /home/hadoop/demo/nlp.sent2kma.py
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

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G  --conf spark.executor.extraLibraryPath=/hdfs/user/hadoop/javisnlp/ /home/hadoop/demo/nlp.sent2kma.py 2> /dev/null'
    run(cmd)


@task
def sent2ner(inpath, outpath, numpartitions, numthreads):
    '''
    fab nlp.sent2ner:/data/sample/sample_hani_sent,/user/hadoop/sample_hani_ner,20,4
    '''
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
	print 'Unauthorized path: %(outpath)s' % locals()
	return
    run('hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null' % locals())
    run('''cat <<EOF > /home/hadoop/demo/nlp.sent2ner.py
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

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G  --conf spark.executor.extraLibraryPath=/hdfs/user/hadoop/javisnlp/ /home/hadoop/demo/nlp.sent2ner.py 2> /dev/null'
    run(cmd)
