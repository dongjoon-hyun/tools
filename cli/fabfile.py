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
CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import *
import hdfs
import spark
import hive
import caffe
import r
import tensorflow
import dolphin
import deepdist
import cuda
import cam
import pdf
import json
import media

import os
import datetime

env.dir = '/log/cli/%s_%s' % (datetime.datetime.now().__format__('%Y%m%d_%H%M'), os.getpid())
env.hosts = ['xxxx']
env.warn_only = True
env.user = 'userid'
env.password = ''
env.output_prefix = False
output['status'] = False
output['stdout'] = True
output['warnings'] = False
output['running'] = False
