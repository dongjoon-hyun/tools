#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.3'

from fabric.api import *

@task
def download(url, outpath=None):
    """
    fab media.download:'https://www.youtube.com/watch?v\=XLVoMd2pnIs',/tmp/youtube/XLVoMd2pnIs
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('youtube-dl -k --all-subs --write-all-thumbnails --restrict-filenames -q %(url)s' % locals(), quiet=True)
        run('hadoop fs -mkdir -p %s' % outpath)
        run('hadoop fs -copyFromLocal * %s' % outpath)
