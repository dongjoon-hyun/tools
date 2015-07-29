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
def text(inpath, count=5):
    """
    fab hdfs.text:/sample/hani_news.head.txt.gz,5
    """
    cmd = '/usr/bin/hadoop fs -text %(inpath)s 2> /dev/null | head -n %(count)s' % locals()
    run(cmd)
