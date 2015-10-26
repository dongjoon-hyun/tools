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
R CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import *


@task
def word_cloud(inpath, topk, outpath, sep='\01'):
    """
    fab r.word_cloud:/user/hadoop/tf_result/part-00000,100,/user/hadoop/wordcloud.png
    """
    run('''cat <<'EOF' > /home/hadoop/demo/r.word_cloud.R
library(wordcloud)
df <- read.table("/hdfs%(inpath)s", header=F, sep="\\001", quote="\\002", stringsAsFactors=F, col.names=c('word','freq'),nrows=%(topk)s)
png("/hdfs%(outpath)s", width=400,height=400)
wordcloud(df$word,df$freq, scale=c(8,.2),min.freq=3,max.words=Inf, random.order=FALSE, rot.per=.15, colors=brewer.pal(8,"Dark2"))
dev.off()
EOF''' % locals())
    cmd = '/usr/bin/Rscript --vanilla /home/hadoop/demo/r.word_cloud.R 2> /dev/null'
    run(cmd)


@task
def sql(inpath, sql):
    """
    fab r.sql:/sample/people.json,'SELECT name FROM people WHERE age <\= 19'
    """
    import os
    table = os.path.splitext(os.path.basename(inpath))[0]
    run('''cat <<'EOF' > /home/hadoop/demo/r.sql.R
suppressMessages(library(SparkR))
sc <- sparkR.init(appName="SparkR SQL")
sqlContext <- sparkRSQL.init(sc)
jsondf <- jsonFile(sqlContext, "%(inpath)s")
registerTempTable(jsondf, "%(table)s")
result <- sql(sqlContext, "%(sql)s")
resultDF <- collect(result)
print(resultDF)
sparkR.stop()
EOF''' % locals())
    cmd = '/opt/spark/bin/spark-submit /home/hadoop/demo/r.sql.R 2> /dev/null | tail -n +4'
    run(cmd)


@task
def summary(inpath):
    """
    fab r.summary:/sample/people.json
    """
    import os
    table = os.path.splitext(os.path.basename(inpath))[0]
    run('''cat <<'EOF' > /home/hadoop/demo/r.summary.R
suppressMessages(library(SparkR))
sc <- sparkR.init(appName="SparkR Summary")
sqlContext <- sparkRSQL.init(sc)
jsondf <- jsonFile(sqlContext, "%(inpath)s")
summary(collect(jsondf))
sparkR.stop()
EOF''' % locals())
    cmd = '/opt/spark/bin/spark-submit /home/hadoop/demo/r.summary.R 2> /dev/null | tail -n +4'
    run(cmd)


@task
def nn_visualize(inpath, formula, hidden, outpath):
    """
    fab r.nn_visualize:/model/r/nn.train,y1~x1+x2+x3,6:12:8,/user/hadoop/nn.png
    """
    hidden = hidden.replace(':', ',')
    run('''cat <<'EOF' > /home/hadoop/demo/r.nn_visualize.R
library(NeuralNetTools)
library(neuralnet)
AND <- c(rep(0, 7), 1)
OR <- c(0, rep(1, 7))
data <- read.table("/hdfs%(inpath)s")
model <- neuralnet(%(formula)s, data, hidden = c(%(hidden)s), rep = 10, err.fct = 'ce', linear.output = FALSE)
png("/hdfs%(outpath)s", width=400,height=400)
par(mar = numeric(4), family = 'serif')
plotnet(model, alpha = 0.6)
dev.off()
EOF''' % locals())
    cmd = '/usr/bin/Rscript --vanilla /home/hadoop/demo/r.nn_visualize.R &> /dev/null'
    run(cmd)
