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
@hosts('50.1.100.101')
def train_mnist(gpu=0,mode='GPU',net='net.prototxt'):
    """
    fab caffe.train_mnist:gpu=0,mode=GPU,net=net.prototxt
    """
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
    """
    fab caffe.predict:bvlc_reference_caffenet,/data/sample/ad_sunglass.png,3
    """
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

@task
def resize_img(inpath,height,width,outpath):
    """
    TODO
    """

@task
def build_lmdb(imgpath,dbpath):
    """
    fab caffe.build_lmdb:/data/image/mnist/jpg/labeled_list.txt,/tmp/mnist.lmdb
    """
    run('''cat <<EOF > /home/hadoop/demo/caffe.build_lmdb.py
# -*- coding: utf-8 -*-
import os
import sys
import lmdb
import pydoop.hdfs as hdfs
import PIL.Image
import numpy as np
import caffe.io
try:
    import caffe_pb2
except ImportError:
    from caffe.proto import caffe_pb2

def load_image(path):
    image = None
    if os.path.exists(path):
        try:
            image = PIL.Image.open(path)
            image.load()
        except IOError as e:
            raise
    else:
        raise Exception('"%%s" not found' %% path)

    if image.mode in ['L', 'RGB']:
        # No conversion necessary
        return image
    elif image.mode in ['1']:
        # Easy conversion to L
        return image.convert('L')
    elif image.mode in ['LA']:
        # Deal with transparencies
        new = PIL.Image.new('L', image.size, 255)
        new.paste(image, mask=image.convert('RGBA'))
        return new
    elif image.mode in ['CMYK', 'YCbCr']:
        # Easy conversion to RGB
        return image.convert('RGB')
    elif image.mode in ['P', 'RGBA']:
        # Deal with transparencies
        new = PIL.Image.new('RGB', image.size, (255, 255, 255))
        new.paste(image, mask=image.convert('RGBA'))
        return new
    else:
        raise errors.LoadImageError, 'Image mode "%%s" not supported' %% image.mode

db = lmdb.open('%(dbpath)s', map_size=1000000000000, map_async=True, max_dbs=0)
count = 1
with hdfs.open('%(imgpath)s') as f:
    for line in f:
        parts = line.strip().split()
        path = parts[0]
        label = int(parts[1])

        image = np.array(load_image('/hdfs' + path))
        if image.ndim == 3:
            # Transpose to (channels, height, width)
            image = image.transpose((2,0,1))
            if image.shape[0] == 3:
                # Channel swap
                image = image[[2,1,0],...]
        elif image.ndim == 2:
            # Add a channels axis
            image = image[np.newaxis,:,:]
        else:
            raise Exception('Image has unrecognized shape: "%%s"' %% image.shape)
        datum = caffe.io.array_to_datum(image, label)

        lmdb_txn = db.begin(write=True)
        lmdb_txn.put("%%s_%%d" %% (path,label), datum.SerializeToString())
        lmdb_txn.commit()
        print count, path, label
        count = count + 1
EOF''' % locals())
    cmd = '/usr/local/bin/python2.7 /home/hadoop/demo/caffe.build_lmdb.py 2> /dev/null'
    #run(cmd)
    run('hadoop fs -mkdir -p %(dbpath)s/' % locals())
    run('hadoop fs -put -f %(dbpath)s/data.mdb %(dbpath)s/' % locals())

@task
def ls_lmdb(dbpath):
    """
    fab caffe.ls_lmdb:/tmp/mnist.lmdb
    """
    run('''cat <<EOF > /home/hadoop/demo/caffe.ls_lmdb.py
import numpy as np
import lmdb
import caffe

env = lmdb.open('%(dbpath)s', lock=False, readonly=True)
count = 1
with env.begin() as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        datum = caffe.proto.caffe_pb2.Datum()
        datum.ParseFromString(value)
        flat_x = np.fromstring(datum.data, dtype=np.uint8)
        x = flat_x.reshape(datum.channels, datum.height, datum.width)
        print count, key, datum.label
        count = count + 1
EOF''' % locals())
    cmd = '/usr/local/bin/python2.7 /home/hadoop/demo/caffe.ls_lmdb.py'
    run(cmd)

