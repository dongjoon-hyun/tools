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
@hosts('50.1.100.101')
def word2vec(inpath,positive,negative):
	'''
	fab deepdist.word2vec:/data/sample/sample_enwiki.head,woman:king,man
	'''
	positive = "'" + positive.replace(":","','") + "'"
	negative = "'" + negative.replace(":","','") + "'"
	run('''cat <<EOF > /home/hadoop/demo/deepdist.word2vec.py
# -*- coding: utf-8 -*-
from deepdist import DeepDist
from gensim.models.word2vec import Word2Vec
from pyspark import SparkConf, SparkContext

sc = SparkContext(appName="DeepDist word2vec")
corpus = sc.textFile('hdfs://gnn-f02-01%(inpath)s').map(lambda s: s.split())

def gradient(model, sentences):  # executes on workers
    syn0, syn1 = model.syn0.copy(), model.syn1.copy()
    model.train(sentences)
    return {'syn0': model.syn0 - syn0, 'syn1': model.syn1 - syn1}

def descent(model, update):      # executes on master
    model.syn0 += update['syn0']
    model.syn1 += update['syn1']

with DeepDist(Word2Vec(corpus.collect())) as dd:
    dd.train(corpus, gradient, descent)
    print dd.model.most_similar(positive=[%(positive)s], negative=[%(negative)s])
EOF''' % locals())
	#cmd = '/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --driver-memory 4G --executor-memory 4G /home/hadoop/demo/deepdist.word2vec.py 2> /dev/null | tail -n 1'
	cmd = '/opt/spark/bin/spark-submit --master local[8] --driver-memory 2G --executor-memory 4G /home/hadoop/demo/deepdist.word2vec.py 2> /dev/null | tail -n 1'
	run(cmd)
