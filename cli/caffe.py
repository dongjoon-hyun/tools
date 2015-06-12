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
def train_mnist(gpu=0,mode='GPU',net='net.prototxt'):
	'''
	fab caffe.train_mnist:gpu=0,mode=GPU,net=net.prototxt
	'''
	run('''cat <<EOF > /home/hadoop/demo/caffe.solver.prototxt
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
	cmd = '/home/hadoop/caffe/distribute/bin/caffe.bin train --solver=/home/hadoop/demo/caffe.solver.prototxt -gpu %(gpu)s' % locals()
	run(cmd)

@task
@hosts('50.1.100.101')
def predict(name, path, topk=5):
	'''
	fab caffe.predict:bvlc_reference_caffenet,/data/sample/ad_sunglass.png,3
	'''
	run('''cat <<EOF > /home/hadoop/demo/caffe.predict.py
# -*- coding: utf-8 -*-
import numpy as np
import sys
sys.path.insert(0, '/home/hadoop/caffe/distribute/python')
import caffe
caffe.set_mode_cpu()

synset_list = []
with open('/hdfs/model/caffe/%(name)s/synset_words.txt', 'r') as f_read:
    for line in f_read.readlines():
        synset_list.append(line[9:].strip())

net = caffe.Classifier('/hdfs/model/caffe/%(name)s/deploy.prototxt', '/hdfs/model/caffe/%(name)s/%(name)s.caffemodel', \
        mean=np.load('/home/hadoop/caffe/distribute/python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1), \
        channel_swap=(2,1,0), \
        raw_scale=255, \
        image_dims=(256, 256))
input_image = caffe.io.load_image('/hdfs%(path)s')
prediction = net.predict([input_image])
predicted_top_classes = list(reversed(prediction[0].argsort()[-%(topk)s:]))
for c in predicted_top_classes:
        print synset_list[c], prediction[0][c]
EOF''' % locals())
	cmd = '/usr/local/bin/python2.7 /home/hadoop/demo/caffe.predict.py 2> /dev/null'
	run(cmd)
