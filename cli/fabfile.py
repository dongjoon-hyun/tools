#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
'''
Intelligence Platform CLI Fabric File
'''

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.1'

from fabric.api import *

env.hosts = ['50.1.100.98']
env.warn_only = True
env.user = 'hadoop'
env.password = '$dnpdjgkdntm'
env.output_prefix = False
output['status'] = False
output['stdout'] = True
output['warnings'] = False
output['running'] = False

def ls(inpath='/'):
	'''
	[HDFS]\tfab ls:/data/sample
	'''
	cmd = '/usr/bin/hadoop fs -ls %(inpath)s 2> /dev/null' % locals()
	run(cmd)

def count(inpath):
	'''
	[HDFS]\tfab count:/data/text/newsgroup
	'''
	cmd = '/usr/bin/hadoop fs -count %(inpath)s 2> /dev/null' % locals()
	run(cmd)

def du(inpath):
	'''
	[HDFS]\tfab du:/data/sample
	'''
	cmd = '/usr/bin/hadoop fs -du -h %(inpath)s 2> /dev/null' % locals()
	run(cmd)

def text(inpath, count=5):
	'''
	[HDFS]\tfab text:/data/sample/hani_news.head.txt.gz,5
	'''
	cmd = '/usr/bin/hadoop fs -text %(inpath)s 2> /dev/null | head -n %(count)s' % locals()
	run(cmd)

def head(inpath, count=5):
	'''
	[Spark]\tfab head:/data/image/imagenet/*.txt,5
	'''
	run('''cat <<EOF > /home/hadoop/demo/head.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Head')
for x in sc.textFile('%(inpath)s').take(%(count)s):
	print x.encode('utf8')
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/head.py 2> /dev/null'
	run(cmd)

def sql(sql='show tables'):
	'''
	[Hive]\tfab sql:'select count(*) from data.news'
	'''
	run('''cat <<EOF > /home/hadoop/demo/hive.sql
%(sql)s
EOF''' % locals())
	cmd = '/usr/bin/hive -S --hiveconf mapred.map.tasks=300 --hiveconf hive.merge.mapfiles=false -f /home/hadoop/demo/hive.sql 2> /dev/null'
	run(cmd)

def sql2(sql):
	'''
	[Spark]\tfab sql2:'select count(*) from data.news'
	'''
	run('''cat <<EOF > /home/hadoop/demo/hivecontext.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import HiveContext
sc = SparkContext(appName='HiveContext')
sqlContext = HiveContext(sc)
for x in sqlContext.sql('%(sql)s').collect():
	print x
EOF''' % locals())
	cmd = 'HADOOP_CONF_DIR=/etc/hive/conf /usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/hivecontext.py 2> /dev/null'
	run(cmd)

def count_line(inpath):
	'''
	[Spark]\tfab count_line:/data/image/imagenet/*.txt
	'''
	run('''cat <<EOF > /home/hadoop/demo/count_line.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Count Line')
print sc.textFile('%(inpath)s').count()
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/count_line.py 2> /dev/null'
	run(cmd)

def count_line_with(inpath, keyword):
	'''
	[Spark]\tfab count_line_with:/data/text/wikipedia/ko*,'<page>'
	'''
	run('''cat <<EOF > /home/hadoop/demo/count_line_with.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Grep')
print sc.textFile('%(inpath)s').filter(lambda line: '%(keyword)s' in line).count()
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/count_line_with.py 2> /dev/null'
	run(cmd)

def grep(inpath, outpath, keyword):
	'''
	[Spark]\tfab grep:/data/text/wikipedia/ko*,/user/hadoop/grep_result,'<page>'
	'''
	run('''cat <<EOF > /home/hadoop/demo/grep.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
sc = SparkContext(appName='Grep')
sc.textFile('%(inpath)s').filter(lambda line: '%(keyword)s' in line).saveAsTextFile('%(outpath)s')
EOF''' % locals())
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/grep.py 2> /dev/null'
	run(cmd)

def tf_ko(inpath,outpath,sep='\01'):
	'''
	[Spark]\tfab tf_ko:/data/text/news/hani/*,/user/hadoop/tf_result
	'''
	if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
		print 'Unauthorized path: %(outpath)s' % locals()
		return
	run('''cat <<EOF > /home/hadoop/demo/tf_ko.py
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
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/tf_ko.py 2> /dev/null'
	run(cmd)

def ngram_ko(n,min,inpath,outpath,sep='\01'):
	'''
	[Spark]\tfab ngram_ko:2,1000,/user/hadoop/tf_result,/user/hadoop/ngram_result
	'''
	if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
		print 'Unauthorized path: %(outpath)s' % locals()
		return
	run('''cat <<EOF > /home/hadoop/demo/ngram_ko.py
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
	cmd = '/usr/bin/spark-submit --num-executors 300 /home/hadoop/demo/ngram_ko.py 2> /dev/null'
	run(cmd)

def word_cloud(inpath):
	'''
	[R]\tfab word_cloud:/user/hadoop/news_word_count.txt
	* output: http://gnn-f05-04/images/wordcloud.png
	'''
	cmd = '/usr/bin/Rscript --vanilla /home/hadoop/demo/word_cloud.R'
	run(cmd)

@hosts('50.1.100.101')
def train_mnist(gpu=0,mode='GPU',net='net.prototxt'):
	'''
	[Caffe]\tfab train_mnist:gpu=0,mode=GPU,net=net.prototxt
	'''
	run('''cat <<EOF > /home/hadoop/solver.prototxt
net: "%(net)s"
test_iter: 100
test_interval: 500
base_lr: 0.01
momentum: 0.9
weight_decay: 0.0005
lr_policy: "inv"
gamma: 0.0001
power: 0.75
display: 100
max_iter: 10000
snapshot: 10000
snapshot_prefix: "tmp"
solver_mode: %(mode)s
EOF''' % locals())
	cmd = '/home/hadoop/caffe/distribute/bin/caffe.bin train --solver=solver.prototxt -gpu %(gpu)s' % locals()
	run(cmd)

@hosts('50.1.100.101')
def classify(name, path, topk=5):
	'''
	[Caffe]\tfab classify:bvlc_reference_caffenet,/data/sample/ad_sunglass.png,3
	'''
	run('''cat <<EOF > /home/hadoop/demo/caffe_classify.py
# -*- coding: utf-8 -*-
import numpy as np
import sys
sys.path.insert(0, '/home/hadoop/caffe/distribute/python')
import caffe
caffe.set_mode_gpu()

synset_list = []
with open('/hdfs/model/caffe/%(name)s/synset_words.txt', 'r') as f_read:
    for line in f_read.readlines():
        synset_list.append(line[9:].strip())

net = caffe.Classifier('/hdfs/model/caffe/%(name)s/deploy.prototxt', '/hdfs/model/caffe/%(name)s/%(name)s.caffemodel', \
        mean=np.load('/home/hadoop/caffe/distribute/python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1), \
        channel_swap=(2,1,0), \
        raw_scale=255, \
        image_dims=(256, 256))
input_image = caffe.io.load_image('/hdfs/%(path)s')
prediction = net.predict([input_image])
predicted_top_classes = list(reversed(prediction[0].argsort()[-%(topk)s:]))
for c in predicted_top_classes:
        print synset_list[c], prediction[0][c]
EOF''' % locals())
	cmd = '/usr/local/bin/python2.7 /home/hadoop/demo/caffe_classify.py 2> /dev/null'
	run(cmd)
