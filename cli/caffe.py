#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'

import os
import pydoop.hdfs as hdfs
from fabric.api import *

@task
@hosts('50.1.100.101')
def train(solver='data/solver.prototxt',net='data/train_val.prototxt',data='/tmp/mnist',model='/tmp/model'):
    """
    fab caffe.train:data/solver.prototxt,data/train_val.prototxt,/tmp/model
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('mkdir train_db')
        run('mkdir val_db')
        put(solver, 'solver.prototxt')
        put(net, 'train_val.prototxt')
        run("sed -i 's/__DIR__/%s/' solver.prototxt" % env.dir.replace('/','\/'))
        run("sed -i 's/__DIR__/%s/' train_val.prototxt" % env.dir.replace('/','\/'))
        run('hadoop fs -get %s/train_db/data.mdb train_db/' % data, quiet=True)
        run('hadoop fs -get %s/val_db/data.mdb val_db/' % data, quiet=True)
        run('hadoop fs -get %s/labels.txt' % data, quiet=True)
        run('/home/hadoop/caffe/distribute/bin/caffe.bin train --solver=solver.prototxt')
        run('hadoop fs -mkdir -p %s' % model)
        run('hadoop fs -put solver.prototxt %s' % model, quiet=True)
        run('hadoop fs -put train_val.prototxt %s' % model, quiet=True)
        run('hadoop fs -put *.caffemodel %s/pretrained.caffemodel' % model, quiet=True)

@task
@hosts('50.1.100.101')
def draw(net,imgpath):
    """
    """

@task
def deploy(model):
    """
    fab caffe.deploy:/tmp/model
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('hadoop fs -get %(model)s/train_val.prototxt' % locals(), quiet=True)
        run('''cat <<EOF > caffe.deploy.py
# -*- coding: utf-8 -*-
import cStringIO
from caffe.proto import caffe_pb2
from google.protobuf import text_format
from google.protobuf import descriptor

net = caffe_pb2.NetParameter()
text_format.Merge(open('train_val.prototxt').read(), net)

out = cStringIO.StringIO()
for f,v in net.ListFields():
    if f.label == descriptor.FieldDescriptor.LABEL_REPEATED:
        for e in v:
            if e.type == 'SoftmaxWithLoss':
                print >>out, """layer {
  name: "prob"
  type: "Softmax"
  bottom: "%%s"
  top: "prob"
}""" %% e.bottom[0]
            elif e.type not in ('Data', 'Accuracy', 'Loss'):
                text_format.PrintField(f, e, out)
    else:
        if f.label == 1: # net name
            print >>out, 'input: "data"'
            print >>out, 'input_dim: 1'
            print >>out, 'input_dim: 1'
            print >>out, 'input_dim: 28'
            print >>out, 'input_dim: 28'
        else:
            text_format.PrintField(f, v, out)
print out.getvalue()
out.close()
EOF''' % locals())
        cmd = '/usr/local/bin/python2.7 caffe.deploy.py > deploy.prototxt 2> /dev/null'
        run(cmd)
        run('hadoop fs -put deploy.prototxt %s' % model, quiet=True)

@task
@hosts('50.1.100.101')
def predict(name, path, color='True',dims='(256,256)',topk=3):
    """
    fab caffe.predict:/model/caffe/bvlc_reference_caffenet,/data/sample/ad_sunglass.png,True,'(256,256)',3
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        img = os.path.basename(path)
        run('hadoop fs -get %(name)s/deploy.prototxt' % locals(), quiet=True)
        run('hadoop fs -get %(name)s/pretrained.caffemodel' % locals(), quiet=True)
        run('hadoop fs -get %(name)s/mean.*' % locals(), quiet=True)
        run('hadoop fs -get %(path)s %(img)s' % locals(), quiet=True)
        run('hadoop fs -get %(name)s/labels.txt' % locals(), quiet=True)
        run('''cat <<EOF > caffe.predict.py
# -*- coding: utf-8 -*-
import sys
import numpy as np
import pydoop.hdfs as hdfs
sys.path.insert(0, '/home/hadoop/caffe/distribute/python')
import caffe
caffe.set_mode_cpu()

labels = []
try:
    with hdfs.open('%(name)s/labels.txt') as f:
        for line in f:
            labels.append(line[9:].strip())
except:
    pass

mean = None
try:
    mean=np.load('mean.npy').mean(1).mean(1)
except:
    pass

channel_swap=None
if True:
    channel_swap=(2,1,0)

net = caffe.Classifier('deploy.prototxt', 'pretrained.caffemodel', \
        mean=mean, \
        channel_swap=channel_swap, \
        raw_scale=255, \
        image_dims=%(dims)s)
input_image = caffe.io.load_image('%(img)s',%(color)s)
prediction = net.predict([input_image])
predicted_top_classes = list(reversed(prediction[0].argsort()[-%(topk)s:]))
for c in predicted_top_classes:
    if len(labels) == 0:
        print c, prediction[0][c]
    else:
        print labels[c], prediction[0][c]
EOF''' % locals())
        #cmd = '/usr/local/bin/python2.7 caffe.predict.py 2> /dev/null'
        cmd = '/usr/local/bin/python2.7 caffe.predict.py'
        run(cmd)

@task
def resize_img(inpath,height,width,outpath):
    """
    TODO
    """

@task
def build_db(imgpath,dbpath,val=0.1):
    """
    fab caffe.build_db:/data/image/mnist/jpg/labeled_list.txt,/tmp/mnist
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > caffe.build_db.py
# -*- coding: utf-8 -*-
import os
import sys
import lmdb
import random
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

train_db = lmdb.open('train_db', map_size=1000000000000, map_async=True, max_dbs=0)
val_db = lmdb.open('val_db', map_size=1000000000000, map_async=True, max_dbs=0)
count = 1
labels = {}
with hdfs.open('%(imgpath)s') as f:
    for line in f:
        parts = line.strip().split()
        path = parts[0]
        if parts[1] in labels:
            label = labels[parts[1]]
        else:
            labels[parts[1]] = len(labels)
            label = labels[parts[1]]

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

        if random.random() < %(val)s:
            db = val_db
            print 'val\t',
        else:
            db = train_db
            print 'train\t',
        lmdb_txn = db.begin(write=True)
        lmdb_txn.put("%%s_%%d" %% (path,label), datum.SerializeToString())
        lmdb_txn.commit()
        print "%%d\t%%s\tLabel:%%-10s\tClassID:%%s" %% (count, path, parts[1], label)
        count = count + 1

f = open('labels.txt', 'w')
for k,v in sorted(labels.items()):
    f.write("%%s\t%%s\\n" %% (k, v))
f.close()
EOF''' % locals())
        #cmd = '/usr/local/bin/python2.7 caffe.build_db.py 2> /dev/null'
        cmd = '/usr/local/bin/python2.7 caffe.build_db.py'
        run(cmd)
        run('hadoop fs -mkdir -p %(dbpath)s/train_db' % locals())
        run('hadoop fs -mkdir -p %(dbpath)s/val_db' % locals())
        run('hadoop fs -put -f train_db/data.mdb %(dbpath)s/train_db' % locals())
        run('hadoop fs -put -f val_db/data.mdb %(dbpath)s/val_db' % locals())
        run('hadoop fs -put -f labels.txt %(dbpath)s/' % locals())

@task
def ls_lmdb(dbpath):
    """
    fab caffe.ls_lmdb:/tmp/mnist.lmdb
    """
    run('''cat <<EOF > /home/hadoop/demo/caffe.ls_lmdb.py
import numpy as np
import lmdb
import caffe

env = lmdb.open('/hdfs%(dbpath)s', lock=False, readonly=True)
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

@task
def classify(model,image):
    """
    fab caffe.classify:/tmp/model,/data/image/mnist/jpg/0/00003.jpg
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > caffe.classify.py
import caffe
from google.protobuf import text_format
from caffe.proto import caffe_pb2

caffe.set_mode_gpu()
net = caffe.Net('/hdfs%(model)s/deploy.prototxt', '/hdfs%(model)s/pretrained.caffemodel', caffe.TEST)

network = caffe_pb2.NetParameter()
with open('/hdfs%(model)s/deploy.prototxt') as infile:
    text_format.Merge(infile.read(), network)

dims = network.input_dim
t = caffe.io.Transformer(inputs = {'data': dims})
t.set_transpose('data', (2,0,1)) # transpose to (channels, height, width)
if dims[1] == 3:
    t.set_channel_swap('data', (2,1,0)) # channel swap
_, channels, height, width = t.inputs['data']

if channels == 3:
    mode = 'RGB'
elif channels == 1:
    mode = 'L'
else:
    raise ValueError('Invalid number for channels: %%s' %% channels)

input_image = caffe.io.load_image('/hdfs%(image)s')
scores = forward_pass([input_image], net, t)
print scores

if image.ndim == 2:
    image = image[:,:,np.newaxis]
    preprocessed = self.get_transformer().preprocess('data', image)
    # reshape net input (if necessary)
    test_shape = (1,) + preprocessed.shape
    if net.blobs['data'].data.shape != test_shape:
        net.blobs['data'].reshape(*test_shape)

    net.blobs['data'].data[...] = preprocessed
    output = net.forward()
    scores = output[net.outputs[-1]].flatten()
    indices = (-scores).argsort()
    predictions = []
    for i in indices:
        predictions.append( (labels[i], scores[i]) )
EOF''' % locals())
        run('python2.7 caffe.classify.py')
