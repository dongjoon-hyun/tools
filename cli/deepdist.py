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
DeepDist CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import task, run, env, cd


@task
def word2vec(inpath, positive, negative):
    """
    fab deepdist.word2vec:/sample/sample_enwiki.head,woman:king,man
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        positive = "'" + positive.replace(":", "','") + "'"
        negative = "'" + negative.replace(":", "','") + "'"
        run('''cat <<EOF > deepdist.word2vec.py
# -*- coding: utf-8 -*-
from deepdist import DeepDist
from gensim.models.word2vec import Word2Vec
from pyspark import SparkConf, SparkContext

sc = SparkContext(appName="DeepDist word2vec")
corpus = sc.textFile('%(inpath)s').map(lambda s: s.split())

def gradient(model, sentences):  # executes on workers
    syn0, syn1 = model.syn0.copy(), model.syn1.copy()
    model.train(sentences)
    return {'syn0': model.syn0 - syn0, 'syn1': model.syn1 - syn1}

def descent(model, update):      # executes on master
    model.syn0 += update['syn0']
    model.syn1 += update['syn1']

with DeepDist(Word2Vec(corpus.collect()), '50.1.100.98:5000') as dd:
    dd.train(corpus, gradient, descent)
    print dd.model.most_similar(positive=[%(positive)s], negative=[%(negative)s])
EOF''' % locals())
        cmd = "/opt/spark/bin/spark-submit --master spark://50.1.100.98:7077 --executor-memory 4G \
deepdist.word2vec.py 2> /dev/null | tail -n 1"
        run(cmd)
