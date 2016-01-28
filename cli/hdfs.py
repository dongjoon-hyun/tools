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
HDFS CLI Fabric File
"""

from fabric.api import *

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.2'


@task
def ls(inpath='/'):
    """
    fab hdfs.ls:/sample
    """
    cmd = '/usr/bin/hadoop fs -ls %(inpath)s 2> /dev/null' % locals()
    run(cmd)


@task
def count(inpath):
    """
    fab hdfs.count:/data/text/newsgroup
    """
    cmd = '/usr/bin/hadoop fs -count %(inpath)s 2> /dev/null' % locals()
    run(cmd)


@task
def du(inpath):
    """
    fab hdfs.du:/sample
    """
    cmd = '/usr/bin/hadoop fs -du -h %(inpath)s 2> /dev/null' % locals()
    run(cmd)


@task
def text(inpath, count=0):
    """
    fab hdfs.text:/sample/hani_news.head.txt.gz,5
    """
    if count == 0:
        cmd = '/usr/bin/hadoop fs -text %(inpath)s 2> /dev/null' % locals()
    else:
        cmd = '/usr/bin/hadoop fs -text %(inpath)s 2> /dev/null | head -n %(count)s' % locals()
    run(cmd)
