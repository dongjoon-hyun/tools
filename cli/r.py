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
def word_cloud(inpath,topk,outpath,sep='\01'):
	'''
	fab r.word_cloud:/user/hadoop/tf_result/part-00000,100,/user/hadoop/wordcloud.png
	'''
	run('''cat <<'EOF' > /home/hadoop/demo/r.word_cloud.R
library(wordcloud)
df <- read.table("/hdfs%(inpath)s", header=F, sep="\\001", quote="\\002", stringsAsFactors=F, col.names=c('word','freq'),nrows=%(topk)s)
png("/hdfs%(outpath)s", width=400,height=400)
wordcloud(df$word,df$freq, scale=c(8,.2),min.freq=3,max.words=Inf, random.order=FALSE, rot.per=.15, colors=brewer.pal(8,"Dark2"))
dev.off()
EOF''' % locals())
	cmd = '/usr/bin/Rscript --vanilla /home/hadoop/demo/r.word_cloud.R 2> /dev/null'
	run(cmd)
