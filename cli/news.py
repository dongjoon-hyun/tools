#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
'''
Intelligence Platform CLI Fabric File
'''

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.2'

from fabric.api import *

'''
Hani Label
[(u'society', 229445),
 (u'opinion', 35368),
 (u'culture', 57530),
 (u'economy', 89948),
 (u'english_edition', 24417),
 (u'science', 5554),
 (u'specialsection', 8514),
 (u'politics', 77644),
 (u'cartoon', 5008),
 (u'infographic', 172),
 (u'international', 59557),
 (u'sports', 60769)]

We use the following lable map.
 0 = society (229445)
 1 = economy (89948)
 2 = politics (77644)
 3 = sports (60769)
 4 = international (59557)
 5 = culture (57530)
'''

@task
def tid(inpath, outpath, col=0):
	'''
	fab news.tid:/data/text/news/hani,/tmp/hani/tid,1
	'''
	run('''cat <<EOF > /home/hadoop/demo/news.tid.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
import re
import string
regex = re.compile(r'[%%s\s0-9a-zA-Z~·]+' %% re.escape(string.punctuation))

sc = SparkContext(appName='Term ID')
data = sc.textFile('%(inpath)s')
tid = data.map(lambda line: line.split('%%c' %% 1)[%(col)s]) \
    .map(lambda line: line.replace(u"‘"," ").replace(u"’"," ").replace(u"“"," ").replace(u"”"," ").replace(u"△"," ").replace(u"◇"," ").replace(u"ㆍ"," ")) \
    .flatMap(lambda line: regex.split(line)) \
    .filter(lambda word: len(word.strip())>1) \
    .map(lambda word: (word,1)) \
    .reduceByKey(lambda x,y: x+y) \
    .filter(lambda (word,count): count>100) \
    .zipWithIndex() \
    .map(lambda ((word,count),index): '%%s%%c%%s%%c%%s' %% (index+1,1,word,1,count)) \
    .saveAsTextFile('%(outpath)s')
EOF''' % locals())
	cmd = '/opt/spark/bin/spark-submit /home/hadoop/demo/news.tid.py 2> /dev/null'
	run(cmd)

@task
def train(inpath, lambda_, model, outpath):
	'''
	fab news.train:/data/text/news/hani/*,1.0,multinomial,/tmp/news
	'''
	run('''cat <<EOF > /home/hadoop/demo/news.train.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint

import re
import string
regex = re.compile(r'[%%s\s0-9a-zA-Z~·]+' %% re.escape(string.punctuation))

catDic = { 'society' : 0.0, 'economy' : 1.0, 'politics': 2.0, 'sports' : 3.0, 'international' : 4.0, 'culture' : 5.0 }
def getLabel(url):
    label = url[27:].split('/')[0]
    if label in catDic.keys():
        return catDic[label]
    else:
        return 99

sc = SparkContext(appName='Naive Bayes Train')
data = sc.textFile('%(inpath)s').filter(lambda line: getLabel(line.split('%%c' %% 1)[0]) != 99).cache()
terms = data.map(lambda line: line.split('%%c' %% 1)[1]) \
    .map(lambda line: line.replace(u"‘"," ").replace(u"’"," ").replace(u"“"," ").replace(u"”"," ").replace(u"△"," ").replace(u"◇"," ").replace(u"ㆍ"," ")) \
    .flatMap(lambda line: regex.split(line)) \
    .filter(lambda word: len(word.strip())>1) \
    .map(lambda word: (word,1)) \
    .reduceByKey(lambda x,y: x+y) \
    .filter(lambda (word,count): count>100) \
    .zipWithIndex() \
    .cache()
terms.map(lambda ((word,count),index): '%%s%%c%%s%%c%%s' %% (index+1,1,word,1,count)) \
    .saveAsTextFile('%(outpath)s/terms')

maxID = terms.values().max() + 1
termDic = sc.broadcast(terms.map(lambda ((word,count),index): (word,index)).collectAsMap())
def getTermID(word):
    try:
        return termDic.value[word]
    except:
        return 0

def parseLine(line):
    parts = line.split('%%c' %% 1)
    label = getLabel(parts[0])
    words = regex.split(parts[1].replace(u"‘"," ").replace(u"’"," ").replace(u"“"," ").replace(u"”"," ").replace(u"△"," ").replace(u"◇"," ").replace(u"ㆍ"," "))
    tids = sorted(set([getTermID(x) for x in words]))
    values = [1] * len(tids)
    features = Vectors.sparse(maxID, tids, values)
    return LabeledPoint(label, features)

#fractions = { 0.0 : 0.16, 1.0 : 0.16, 2.0 : 0.16, 3.0 : 0.16, 4.0 : 0.16, 5.0 : 0.16 }
fractions = { 0.0 : 0.25, 1.0 : 0.64, 2.0 : 0.74, 3.0 : 0.95, 4.0 : 0.97, 5.0 : 1.0 }
labeledPoints = data.map(lambda line: (getLabel(line.split('%%c' %% 1)[0]), line)) \
    .sampleByKey(False, fractions) \
    .map(lambda (x,y): y) \
    .map(parseLine)
labeledPoints.saveAsTextFile('%(outpath)s/docs')

model = NaiveBayes.train(labeledPoints, %(lambda_)s)
model.save(sc, '%(outpath)s/model')

predictedSample = labeledPoints.map(lambda p: (p.label, model.predict(p.features)))
accuracy = 1.0 * predictedSample.filter(lambda (x,y): x == y).count() / predictedSample.count()
print 'Model Accuracy(self): ', accuracy

predictedAll = data.map(parseLine).map(lambda p: (p.label, model.predict(p.features)))
accuracy = 1.0 * predictedAll.filter(lambda (x,y): x == y).count() / predictedAll.count()
print 'Model Accuracy(all): ', accuracy
EOF''' % locals())
	cmd = '/opt/spark/bin/spark-submit --driver-memory 2G --executor-memory 2G /home/hadoop/demo/news.train.py 2> /dev/null'
	run(cmd)

@task
def predict(model, text):
	'''
	fab news.predict:/model/spark/news,'최근 전국 아파트 분양 시장의'
	'''
	run('''cat <<EOF > /home/hadoop/demo/news.predict.py
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.mllib.classification import NaiveBayesModel
from pyspark.mllib.linalg import Vectors

import re
import string
regex = re.compile(r'[%%s\s0-9a-zA-Z~·]+' %% re.escape(string.punctuation))

def parseMap(line):
    parts = line.split('%%c' %% 1)
    index = int(parts[0])
    word = parts[1]
    return (word,index)

sc = SparkContext(appName='Naive Bayes Predict')
model = NaiveBayesModel.load(sc, '%(model)s/model')
termDic = sc.textFile('%(model)s/terms').map(parseMap).collectAsMap()
maxID = len(termDic)

def getTermID(word):
    try:
        return termDic[word]
    except:
        return 0

def parseLine(line):
    words = regex.split(line.replace(u"‘"," ").replace(u"’"," ").replace(u"“"," ").replace(u"”"," ").replace(u"△"," ").replace(u"◇"," ").replace(u"ㆍ"," "))
    tids = sorted(set([getTermID(x) for x in words]))
    values = [1] * len(tids)
    features = Vectors.sparse(maxID, tids, values)
    return features

label = model.predict(parseLine('%(text)s'.decode('utf8')))
catDic = { 'society' : 0.0, 'economy' : 1.0, 'politics': 2.0, 'sports' : 3.0, 'international' : 4.0, 'culture' : 5.0 }
for k,v in catDic.iteritems():
    if label == v:
        print k
EOF''' % locals())
	cmd = '/opt/spark/bin/spark-submit /home/hadoop/demo/news.predict.py 2> /dev/null | head -n 1'
	run(cmd)
