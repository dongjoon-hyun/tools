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
def mnist(inpath):
    """
    fab tensorflow.mnist:/sample/mnist/
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > tensorflow.mnist.py
# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# Data.
mnist = input_data.read_data_sets("%(inpath)s", one_hot=True)

# Model.
x = tf.placeholder(tf.float32, [None, 784])
#W = tf.Variable(tf.zeros([784, 10]))
W = tf.Variable(tf.truncated_normal([784, 10], stddev=0.1))
#b = tf.Variable(tf.zeros([10]))
b = tf.Variable(tf.constant(0.1, shape=[10]))
y = tf.nn.softmax(tf.matmul(x, W) + b)

# Train.
y_ = tf.placeholder(tf.float32, [None, 10])
cross_entropy = -tf.reduce_sum(y_ * tf.log(y))
train_step = tf.train.AdamOptimizer(0.001).minimize(cross_entropy)

# Start.
sess = tf.Session()
sess.run(tf.initialize_all_variables())
for i in range(2000):
  batch_xs, batch_ys = mnist.train.next_batch(500)
  sess.run(train_step, {x: batch_xs, y_: batch_ys})

# Test.
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(sess.run(accuracy, {x: mnist.test.images, y_: mnist.test.labels}))
EOF''' % locals())
        cmd = '/usr/bin/env python tensorflow.mnist.py 2> /dev/null | grep -v Extracting '
        run(cmd)
