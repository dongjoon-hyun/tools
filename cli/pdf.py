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
PDF CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import task, run, env, cd


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
