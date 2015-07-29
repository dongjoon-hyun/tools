#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.2'

from fabric.api import *
import hdfs
import spark
import hive
import caffe
import r
import snu
import nlp
import deepdist
import news
import cuda
import cam
import pdf
import json

import os
import datetime

env.dir = '/log/tip/%s_%s' % (datetime.datetime.now().__format__('%Y%m%d_%H%M'), os.getpid())
env.hosts = ['50.1.100.98']
env.warn_only = True
env.user = 'hadoop'
env.password = '$dnpdjgkdntm'
env.output_prefix = False
output['status'] = False
output['stdout'] = True
output['warnings'] = False
output['running'] = False
