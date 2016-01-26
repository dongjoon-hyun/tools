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
Tensorflow CLI Fabric File
(Based on TensorFlow Website)[https://www.tensorflow.org]
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import *

@task
def lm(inpath, step, maxiter):
    """
    fab tensorflow.lm:/sample/sample_regression,0.1,100
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > tensorflow.lm.py
# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np

# Data. (Note: -1 < x < 1)
data = np.loadtxt('%(inpath)s')
x_ = data[...,0]
y_ = data[...,1]
print len(data), 'instances loaded.'

# Model.
W = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
b = tf.Variable(tf.zeros([1]))
y = W * x_ + b

# Train.
train = tf.train.GradientDescentOptimizer(%(step)s).minimize(tf.reduce_mean(tf.square(y - y_)))

# Start.
sess = tf.Session()
sess.run(tf.initialize_all_variables())
for step in xrange(%(maxiter)s):
    sess.run(train)
print "%%.2f * x + %%.2f" %% (sess.run(W), sess.run(b))
EOF''' % locals())
        cmd = '/usr/bin/env python tensorflow.lm.py 2> /dev/null'
        run(cmd)


@task
def mnist(inpath,outpath):
    """
    fab tensorflow.mnist:/sample/mnist,/tmp/mnist
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > tensorflow.mnist.py
# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# Data.
mnist = input_data.read_data_sets("%(inpath)s/", one_hot=True)

# Model.
x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])
W = tf.Variable(tf.truncated_normal([784, 10], stddev=0.1))
b = tf.Variable(tf.constant(0.1, shape=[10]))
y = tf.nn.softmax(tf.matmul(x, W) + b)

# Train.
cross_entropy = -tf.reduce_sum(y_ * tf.log(y))
train_step = tf.train.AdamOptimizer(0.001).minimize(cross_entropy)

# Start.
sess = tf.Session()
sess.run(tf.initialize_all_variables())
for i in range(4000):
  batch_xs, batch_ys = mnist.train.next_batch(500)
  sess.run(train_step, {x: batch_xs, y_: batch_ys})

# Test.
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(sess.run(accuracy, {x: mnist.test.images, y_: mnist.test.labels}))

# Save.
saver = tf.train.Saver()
saver.save(sess, "%(outpath)s/model", 0)
EOF''' % locals())
        cmd = '/usr/bin/env python tensorflow.mnist.py 2> /dev/null | grep -v Extracting '
        run(cmd)


@task()
def predict(inpath, model):
    """
    fab tensorflow.predict:/sample/mnist,/tmp/mnist/model-0
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > tensorflow.predict.py
# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# Model.
x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])
W = tf.Variable(tf.truncated_normal([784, 10], stddev=0.1))
b = tf.Variable(tf.constant(0.1, shape=[10]))
y = tf.nn.softmax(tf.matmul(x, W) + b)

# Load pre-built variables.
sess = tf.Session()
saver = tf.train.Saver()
saver.restore(sess, "%(model)s")

# Predict.
mnist = input_data.read_data_sets("%(inpath)s/", one_hot=True)
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(sess.run(accuracy, {x: mnist.test.images, y_: mnist.test.labels}))
EOF''' % locals())
        cmd = '/usr/bin/env python tensorflow.predict.py'
        run(cmd)


@task
def mnist_conv(inpath, epoch, outpath):
    """
    fab tensorflow.mnist_conv:/sample/mnist,1,/tmp/mnist_conv
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > tensorflow.mnist_conv.py
import sys
import tensorflow.python.platform
from tensorflow.models.image.mnist.convolutional import extract_data, extract_labels, error_rate

import numpy
from six.moves import xrange
import tensorflow as tf

IMAGE_SIZE = 28
NUM_CHANNELS = 1
PIXEL_DEPTH = 255
NUM_LABELS = 10
VALIDATION_SIZE = 5000
BATCH_SIZE = 1024
EVAL_BATCH_SIZE = 1024

train_data = extract_data('%(inpath)s/train-images-idx3-ubyte.gz', 60000)
train_labels = extract_labels('%(inpath)s/train-labels-idx1-ubyte.gz', 60000)
test_data = extract_data('%(inpath)s/t10k-images-idx3-ubyte.gz', 10000)
test_labels = extract_labels('%(inpath)s/t10k-labels-idx1-ubyte.gz', 10000)

validation_data = train_data[:VALIDATION_SIZE, ...]
validation_labels = train_labels[:VALIDATION_SIZE]
train_data = train_data[VALIDATION_SIZE:, ...]
train_labels = train_labels[VALIDATION_SIZE:]
train_size = train_labels.shape[0]

train_data_node = tf.placeholder(tf.float32, shape=(BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))
train_labels_node = tf.placeholder(tf.float32, shape=(BATCH_SIZE, NUM_LABELS))
eval_data = tf.placeholder( tf.float32, shape=(EVAL_BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))

conv1_weights = tf.Variable( tf.truncated_normal([5, 5, NUM_CHANNELS, 32], stddev=0.1))
conv1_biases = tf.Variable(tf.zeros([32]))
conv2_weights = tf.Variable(tf.truncated_normal([5, 5, 32, 64], stddev=0.1))
conv2_biases = tf.Variable(tf.constant(0.1, shape=[64]))
fc1_weights = tf.Variable( tf.truncated_normal( [IMAGE_SIZE // 4 * IMAGE_SIZE // 4 * 64, 512], stddev=0.1))
fc1_biases = tf.Variable(tf.constant(0.1, shape=[512]))
fc2_weights = tf.Variable( tf.truncated_normal([512, NUM_LABELS], stddev=0.1))
fc2_biases = tf.Variable(tf.constant(0.1, shape=[NUM_LABELS]))

def model(data, train=False):
  conv = tf.nn.conv2d(data, conv1_weights, strides=[1, 1, 1, 1], padding='SAME')
  relu = tf.nn.relu(tf.nn.bias_add(conv, conv1_biases))
  pool = tf.nn.max_pool(relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
  conv = tf.nn.conv2d(pool, conv2_weights, strides=[1, 1, 1, 1], padding='SAME')
  relu = tf.nn.relu(tf.nn.bias_add(conv, conv2_biases))
  pool = tf.nn.max_pool(relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
  pool_shape = pool.get_shape().as_list()
  reshape = tf.reshape( pool, [pool_shape[0], pool_shape[1] * pool_shape[2] * pool_shape[3]])
  hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights) + fc1_biases)
  if train:
    hidden = tf.nn.dropout(hidden, 0.5)
  return tf.matmul(hidden, fc2_weights) + fc2_biases

logits = model(train_data_node, True)
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits, train_labels_node))
regularizers = (tf.nn.l2_loss(fc1_weights) + tf.nn.l2_loss(fc1_biases) + tf.nn.l2_loss(fc2_weights) + tf.nn.l2_loss(fc2_biases))
loss += 5e-4 * regularizers

batch = tf.Variable(0)
learning_rate = tf.train.exponential_decay( 0.01, batch * BATCH_SIZE, train_size, 0.95, staircase=True)
optimizer = tf.train.MomentumOptimizer(learning_rate, 0.9).minimize(loss, global_step=batch)
train_prediction = tf.nn.softmax(logits)
eval_prediction = tf.nn.softmax(model(eval_data))

def eval_in_batches(data, sess):
  size = data.shape[0]
  predictions = numpy.ndarray(shape=(size, NUM_LABELS), dtype=numpy.float32)
  for begin in xrange(0, size, EVAL_BATCH_SIZE):
    end = begin + EVAL_BATCH_SIZE
    if end <= size:
      predictions[begin:end, :] = sess.run(eval_prediction, feed_dict={eval_data: data[begin:end, ...]})
    else:
      batch_predictions = sess.run( eval_prediction, feed_dict={eval_data: data[-EVAL_BATCH_SIZE:, ...]})
      predictions[begin:, :] = batch_predictions[begin - size:, :]
  return predictions

with tf.Session() as sess:
  tf.initialize_all_variables().run()
  for step in xrange(int(%(epoch)s * train_size) // BATCH_SIZE):
    offset = (step * BATCH_SIZE) %% (train_size - BATCH_SIZE)
    batch_data = train_data[offset:(offset + BATCH_SIZE), ...]
    batch_labels = train_labels[offset:(offset + BATCH_SIZE)]
    feed_dict = {train_data_node: batch_data, train_labels_node: batch_labels}
    _, l, lr, predictions = sess.run([optimizer, loss, learning_rate, train_prediction], feed_dict=feed_dict)
    print('%%.1f' %% error_rate(eval_in_batches(batch_data, sess), batch_labels))
  print('%%.1f' %% error_rate(eval_in_batches(test_data, sess), test_labels))

  # Save.
  saver = tf.train.Saver()
  saver.save(sess, "%(outpath)s/model", 0)
EOF''' % locals())
        cmd = '/usr/bin/env python tensorflow.mnist_conv.py 2> /dev/null'
        run(cmd)
