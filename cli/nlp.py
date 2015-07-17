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
def doc2kma(inpath, outpath, numpartitions, numthreads, sep = '\01'):
    '''
    fab nlp.doc2kma:/data/sample/sample_hani,/user/hadoop/sample_hani_kma,20,4
    '''
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return 
    run('hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null' % locals())
    run('''cat <<EOF > /home/hadoop/demo/nlp.doc2kma.py
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
conf.setAppName('doc2kma')
sc = SparkContext(conf=conf)

scNLPModuleName = sc.broadcast(nlpModuleName)
scNumThreads = sc.broadcast(numThreads)

def runNLP(pindex, lines):
    import sys
    sys.path.append('/hdfs/user/hadoop/javisnlp/')
    from JavisNLP import JavisNLP
    nlp = JavisNLP()
    nlp.init('/hdfs/user/hadoop/javisnlp/config/NLU.cfg')
    lines = list(lines)
    others = [s[:-1] for s in lines]
    sents = [s[-1] for s in lines]    
    results = nlp.runBatch(sents, scNumThreads.value, scNLPModuleName.value)
    return [tuple(list(t[0]) + [t[1]]) for t in zip(others, results)]
   
for f in sc.wholeTextFiles(inputFileName).map(lambda (f,c): f).collect():
    print f
    sents = sc.textFile(f) \
        .map(lambda line: line.split('%%c' %% (1))) \
        .map(lambda line: tuple(list(line[:-1]) + ['.\\n'.join(t.strip() for t in line[-1].split('.'))]))
    
    if numPartitions >= 1 and numPartitions <= 60:
        print 'Repartition: ' + str(numPartitions)
        sents = sents.repartition(numPartitions).cache()
    else:
        print 'NumPartitions: ' + str(sents.getNumPartitions())
    
    results = sents.mapPartitionsWithIndex(runNLP)
    results.cache()
    print results.count()
    results.map(lambda line: tuple(list(line[:-1]) + [' '.join(line[-1].split('\\n'))])).map(lambda line: ('%%c' %% (1)).join(line)).repartition(1).saveAsTextFile(outputFileName + '/' + f.split('/')[-1])
print 'Completed: ' + outputFileName
EOF''' % locals())

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G --conf spark.cores.max=240 --conf spark.executor.extraLibraryPath=/hdfs/user/hadoop/javisnlp/ /home/hadoop/demo/nlp.doc2kma.py 2> /dev/null'
    run(cmd)
    
    
@task
def doc2ner(inpath, outpath, numpartitions, numthreads, sep = '\01'):
    '''
    fab nlp.doc2ner:/data/sample/sample_hani,/user/hadoop/sample_hani_ner,20,4
    '''
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return 
    run('hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null' % locals())
    run('''cat <<EOF > /home/hadoop/demo/nlp.doc2ner.py
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
conf.setAppName('doc2ner')
sc = SparkContext(conf=conf)

scNLPModuleName = sc.broadcast(nlpModuleName)
scNumThreads = sc.broadcast(numThreads)

def runNLP(pindex, lines):
    import sys
    sys.path.append('/hdfs/user/hadoop/javisnlp/')
    from JavisNLP import JavisNLP
    nlp = JavisNLP()
    nlp.init('/hdfs/user/hadoop/javisnlp/config/NLU.cfg')
    lines = list(lines)
    others = [s[:-1] for s in lines]
    sents = [s[-1] for s in lines]    
    results = nlp.runBatch(sents, scNumThreads.value, scNLPModuleName.value)
    return [tuple(list(t[0]) + [t[1]]) for t in zip(others, results)]
   
for f in sc.wholeTextFiles(inputFileName).map(lambda (f,c): f).collect():
    print f
    sents = sc.textFile(f) \
        .map(lambda line: line.split('%%c' %% (1))) \
        .map(lambda line: tuple(list(line[:-1]) + ['.\\n'.join(t.strip() for t in line[-1].split('.'))]))
    
    if numPartitions >= 1 and numPartitions <= 60:
        print 'Repartition: ' + str(numPartitions)
        sents = sents.repartition(numPartitions).cache()
    else:
        print 'NumPartitions: ' + str(sents.getNumPartitions())
    
    results = sents.mapPartitionsWithIndex(runNLP)
    results.cache()
    print results.count()
    results.map(lambda line: tuple(list(line[:-1]) + [' '.join(line[-1].split('\\n'))])).map(lambda line: ('%%c' %% (1)).join(line)).repartition(1).saveAsTextFile(outputFileName + '/' + f.split('/')[-1])
print 'Completed: ' + outputFileName
EOF''' % locals())

    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G --conf spark.cores.max=240 --conf spark.executor.extraLibraryPath=/hdfs/user/hadoop/javisnlp/ /home/hadoop/demo/nlp.doc2ner.py 2> /dev/null'
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
    
    
@task
def kma(inputText, formatter):
    '''
    fab nlp.kma:'서울의 인구는 1000만명이다.',kma(or cls)
    '''
    run('''cat <<EOF > /home/hadoop/demo/nlp.kma.py
# -*- encoding: utf-8 -*-
import sys

input = '%(inputText)s'.decode('utf-8')

def runNLP(inputText, nlpModuleName):
    import sys
    sys.path.append('/hdfs/user/hadoop/javisnlp/')
    from JavisNLP import JavisNLP
    nlp = JavisNLP()
    nlp.init('/hdfs/user/hadoop/javisnlp/config/NLU.cfg')
    nlp.setModuleFlow(['KMA'])
    nlp.setFormatter(nlpModuleName)
    return nlp.run(inputText)

result = runNLP(input, '%(formatter)s')
print result
EOF''' % locals())

    cmd = 'export LD_LIBRARY_PATH=/hdfs/user/hadoop/javisnlp/:$LD_LIBRARY_PATH && python2.7 /home/hadoop/demo/nlp.kma.py 2> /dev/null'
    run(cmd)    


@task
def kner(inputText, formatter):
    '''
    fab nlp.kner:'서울의 인구는 1000만명이다.',ner(or cls)
    '''
    run('''cat <<EOF > /home/hadoop/demo/nlp.kner.py
# -*- encoding: utf-8 -*-
import sys

input = '%(inputText)s'.decode('utf-8')

def runNLP(inputText, nlpModuleName):
    import sys
    sys.path.append('/hdfs/user/hadoop/javisnlp/')
    from JavisNLP import JavisNLP
    nlp = JavisNLP()
    nlp.init('/hdfs/user/hadoop/javisnlp/config/NLU.cfg')
    nlp.setModuleFlow(['KMA', 'NER'])
    nlp.setFormatter(nlpModuleName)
    return nlp.run(inputText)

result = runNLP(input, '%(formatter)s')
print result
EOF''' % locals())

    cmd = 'export LD_LIBRARY_PATH=/hdfs/user/hadoop/javisnlp/:$LD_LIBRARY_PATH && python2.7 /home/hadoop/demo/nlp.kner.py 2> /dev/null'
    run(cmd)


@task
def word2vec_train(inpath, outpath, numpartitions, numiterations):
    '''
    fab nlp.word2vec_train:/data/sample/sample_hani_kma,/user/hadoop/sample_hani_wordvec,20,1
    '''
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
	return
    run('hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null' % locals())
    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --class SparkWord2VecTrain --num-executors 120 --driver-memory 4G --executor-memory 4G --conf spark.akka.frameSize=200 /hdfs/user/hadoop/demo/nlp/sparkword2vec_2.10-1.0.jar %(inpath)s %(outpath)s %(numpartitions)s %(numiterations)s 2> /dev/null' % locals()
    run(cmd)
    

@task
def word2vec_test(modelpath, queryword, topn):
    '''
    fab nlp.word2vec_test:/data/sample/sample_hani_wordvec,서울,10
    '''
    cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --class SparkWord2VecTest --num-executors 120 --driver-memory 4G --executor-memory 4G --conf spark.akka.frameSize=200 /hdfs/user/hadoop/demo/nlp/sparkword2vec_2.10-1.0.jar %(modelpath)s %(queryword)s %(topn)s  2> /dev/null' % locals()
    run(cmd)
