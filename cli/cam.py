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
@hosts('127.0.0.1')
def view():
    '''
    fab cam.view
    '''
    import cv2
    import numpy as np
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
def capture(outpath, max_count='10'):
    '''
    fab cam.capture:/tmp/cam1,10
    '''
    max_count = int(max_count)
    import os
    import cv2
    import copy
    import numpy as np
    import pydoop.hdfs as hdfs
    import threading

    cv2.namedWindow('Window1')
    vc = cv2.VideoCapture()
    vc.open(0)
    skip = 50
    max_count = max_count * skip
    basename = os.path.basename(outpath)
    count = 1
    hdfs.mkdir('hdfs://gnn-f02-01' + outpath)
    while True:
        retval, image = vc.read()
        try:
            if count % skip == 0:
                tmpImage = copy.copy(image)
                filename = '%05d.jpg' % (count/skip)
                hdfspath = 'hdfs://gnn-f02-01%(outpath)s/%(filename)s' % locals()
                cv2.putText(tmpImage, filename, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
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
        count = count + 1
        if max_count > 0 and count > max_count:
            break
    vc.release()
    cv2.destroyWindow('Window1')
