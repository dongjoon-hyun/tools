#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.2'

from fabric.api import *


@task
def pagerank(inpath, outpath, threshold, maxiter, damping):
    """
    fab snu.pagerank:/sample/sample_pagerank,/user/hadoop/pagerank_result,0.01,10,0.85
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('''cat <<'EOF' > /home/hadoop/demo/snu.pagerank.sh
java -cp $YARN_CONF_DIR:/home/hadoop/dolphin/target/dolphin-0.1-SNAPSHOT-shaded.jar:/data1/cloudera/parcels/CDH/jars/* -Djava.util.logging.config.class=org.apache.reef.util.logging.Config edu.snu.reef.dolphin.examples.ml.algorithms.graph.PageRankREEF -convThr %(threshold)s -maxIter %(maxiter)s -dampingFactor %(damping)s -split 2 -input %(inpath)s -output /tmp/pagerank &> /dev/null
hadoop fs -rm -r -f -skipTrash %(outpath)s &> /dev/null
hadoop fs -mkdir %(outpath)s
hadoop fs -mv /tmp/pagerank/rank/CtrlTask-0 %(outpath)s
EOF''' % locals())
    cmd = '/bin/bash /home/hadoop/demo/snu.pagerank.sh'
    run(cmd)


@task
def em(inpath, outpath, cluster, threshold, maxiter):
    """
    fab snu.em:/sample/sample_cluster,/user/hadoop/em_result,4,0.01,20
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('''cat <<'EOF' > /home/hadoop/demo/snu.em.sh
java -cp $YARN_CONF_DIR:/home/hadoop/dolphin/target/dolphin-0.1-SNAPSHOT-shaded.jar:/data1/cloudera/parcels/CDH/jars/* -Djava.util.logging.config.class=org.apache.reef.util.logging.Config edu.snu.reef.dolphin.examples.ml.algorithms.clustering.em.EMREEF -numCls %(cluster)s -convThr %(threshold)s -maxIter %(maxiter)s -split 4 -input %(inpath)s -output %(outpath)s &> /dev/null
EOF''' % locals())
    cmd = '/bin/bash /home/hadoop/demo/snu.em.sh'
    run(cmd)


@task
def kmeans(inpath, outpath, cluster, threshold, maxiter):
    """
    fab snu.kmeans:/sample/sample_cluster,/user/hadoop/kmeans_result,4,0.01,20
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('''cat <<'EOF' > /home/hadoop/demo/snu.kmeans.sh
java -cp $YARN_CONF_DIR:/home/hadoop/dolphin/target/dolphin-0.1-SNAPSHOT-shaded.jar:/data1/cloudera/parcels/CDH/jars/* -Djava.util.logging.config.class=org.apache.reef.util.logging.Config edu.snu.reef.dolphin.examples.ml.algorithms.clustering.kmeans.KMeansREEF -numCls %(cluster)s -convThr %(threshold)s -maxIter %(maxiter)s -split 4 -input %(inpath)s -output %(outpath)s &> /dev/null
EOF''' % locals())
    cmd = '/bin/bash /home/hadoop/demo/snu.kmeans.sh'
    run(cmd)


@task
def lm(inpath, outpath, dim, step, lam, maxiter):
    """
    fab snu.lm:/sample/sample_regression,/user/hadoop/lm_result,3,0.001,0.1,20
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('''cat <<'EOF' > /home/hadoop/demo/snu.lm.sh
java -cp $YARN_CONF_DIR:/home/hadoop/dolphin/target/dolphin-0.1-SNAPSHOT-shaded.jar:/data1/cloudera/parcels/CDH/jars/* -Djava.util.logging.config.class=org.apache.reef.util.logging.Config edu.snu.reef.dolphin.examples.ml.algorithms.regression.LinearRegREEF -dim %(dim)s -stepSize %(step)s -lambda %(lam)s -maxIter %(maxiter)s -split 4 -input %(inpath)s -output %(outpath)s &> /dev/null
EOF''' % locals())
    cmd = '/bin/bash /home/hadoop/demo/snu.lm.sh'
    run(cmd)


@task
def lr(inpath, outpath, dim, step, lam, maxiter):
    """
    fab snu.lr:/sample/sample_classification,/user/hadoop/lr_result,3,0.00001,0.1,20
    """
    if not (outpath.startswith('/tmp/') or outpath.startswith('/user/hadoop/')):
        print 'Unauthorized path: %(outpath)s' % locals()
        return
    run('''cat <<'EOF' > /home/hadoop/demo/snu.lr.sh
java -cp $YARN_CONF_DIR:/home/hadoop/dolphin/target/dolphin-0.1-SNAPSHOT-shaded.jar:/data1/cloudera/parcels/CDH/jars/* -Djava.util.logging.config.class=org.apache.reef.util.logging.Config edu.snu.reef.dolphin.examples.ml.algorithms.classification.LogisticRegREEF -dim %(dim)s -stepSize %(step)s -lambda %(lam)s -maxIter %(maxiter)s -split 4 -input %(inpath)s -output %(outpath)s &> /dev/null
EOF''' % locals())
    cmd = '/bin/bash /home/hadoop/demo/snu.lr.sh'
    run(cmd)
