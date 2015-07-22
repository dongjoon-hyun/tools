#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
'''
Intelligence Platform CLI Fabric File
'''

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.3'

from fabric.api import *

@task
@hosts('50.1.100.98')
def text(inpath, outpath=None):
    '''
    fab pdf.text:/sample/report.pdf
    '''
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        if outpath == None:
            run('pdf2txt.py /hdfs%(inpath)s 2> /dev/null' % locals())
            print ''
        else:
            run('pdf2txt.py /hdfs%(inpath)s > /hdfs%(outpath)s 2> /dev/null' % locals())

@task
@hosts('50.1.100.98')
def image(inpath, outpath=None):
    '''
    fab pdf.image:/sample/report.pdf,/tmp/extracted
    '''
    run('mkdir %s' % env.dir)
    import os
    basename = os.path.basename(inpath).split('.')[0]
    with cd(env.dir):
        if outpath == None:
            run('pdfimages -q /hdfs%(inpath)s %(basename)s 2> /dev/null' % locals())
        else:
            run('pdfimages -q /hdfs%(inpath)s %(basename)s 2> /dev/null' % locals())
            run('mkdir /hdfs%(outpath)s' % locals())
            run('for f in `ls *.ppm`; do ppm2tiff $f /hdfs%(outpath)s/${f/.ppm/.jpg}; done' % locals())
