#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Camera CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import task, hosts


@task
@hosts('127.0.0.1')
def view():
    """
    fab cam.view
    """
    import cv2

    cv2.namedWindow('Window1')
    vc = cv2.VideoCapture()
    vc.open(0)
    while True:
        retval, image = vc.read()
        cv2.imshow('Windows1', image)
        try:
            cv2.waitKey(1)
        except KeyboardInterrupt:
            break
    vc.release()
    cv2.destroyWindow('Window1')


@task
@hosts('127.0.0.1')
def capture(outpath, max_count='3'):
    """
    fab cam.capture:/tmp/cam1,3
    """
    max_count = int(max_count)
    import os
    import cv2
    import copy
    import pydoop.hdfs as hdfs

    cv2.namedWindow('Window1')
    vc = cv2.VideoCapture()
    vc.open(0)
    skip = 50
    max_count *= skip
    basename = os.path.basename(outpath)
    count = 1
    hdfs.mkdir('hdfs://gnn-f02-01' + outpath)
    while True:
        retval, image = vc.read()
        try:
            if count % skip == 0:
                tmpImage = copy.copy(image)
                filename = '%05d.jpg' % (count / skip)
                hdfspath = 'hdfs://gnn-f02-01%(outpath)s/%(filename)s' % locals()
                cv2.putText(tmpImage, filename, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                cv2.imshow('Windows1', tmpImage)
                cv2.waitKey(1)
                cv2.imwrite(basename + '_' + filename, image)
                hdfs.put(basename + '_' + filename, hdfspath)
                print basename + '_' + filename, hdfspath
            else:
                cv2.imshow('Windows1', image)
                cv2.waitKey(1)
        except KeyboardInterrupt:
            break
        count += 1
        if 0 < max_count < count:
            break
    vc.release()
    cv2.destroyWindow('Window1')
