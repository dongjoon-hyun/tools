#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Intelligence Platform CLI Fabric File
"""

from fabric.api import *

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'


@task
def text(inpath, outpath=None):
    """
    fab pdf.text:/sample/report.pdf
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        if outpath:
            run('pdf2txt.py /hdfs%(inpath)s > /hdfs%(outpath)s' % locals(), quiet=True)
        else:
            run('pdf2txt.py /hdfs%(inpath)s 2> /dev/null' % locals())
            print ''


@task
def image(inpath, outpath):
    """
    fab pdf.image:/sample/report.pdf,/tmp/extracted
    """
    run('mkdir %s' % env.dir)
    import os
    basename = os.path.basename(inpath).split('.')[0]
    with cd(env.dir):
        run('pdfimages -q /hdfs%(inpath)s %(basename)s' % locals())
        run('mkdir /hdfs%(outpath)s' % locals())
        run('for f in `ls *.ppm`; do ppm2tiff $f /hdfs%(outpath)s/${f/.ppm/.jpg}; done' % locals())
