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
        run('youtube-dl -k --all-subs --write-all-thumbnails --write-description --write-info-json --restrict-filenames -q %(url)s' % locals(), quiet=True)
        run('hadoop fs -mkdir -p %s' % outpath)
        run('hadoop fs -copyFromLocal * %s' % outpath)

@task
def srt_to_json(inpath, outpath):
    """
    fab media.srt_to_json:/data/video/youtube/3_AZ5R2SC88/*.en.srt
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<EOF > srt_to_json.py
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os
import glob
import pysrt
import json

script = glob.glob('/hdfs%(inpath)s')
srt = pysrt.open(script[0])
dic = map(lambda x: {'index':x.index,'start':str(x.start.to_time()),'end':str(x.end.to_time()),'text':x.text}, srt)
with open('/hdfs%(outpath)s', 'w') as outfile:
    json.dump(dic, outfile, sort_keys=True, indent=4, separators=(',', ': '))
EOF''' % locals())
        run('python2.7 srt_to_json.py')

@task
def gen_meta(inpath):
    """
    fab media.gen_meta:/data/video/youtube/3_AZ5R2SC88
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('rm /hdfs%(inpath)s/meta.json' % locals(), quiet=True)
        run('''cat <<EOF > gen_meta.py
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os
import glob
import pysrt
import json

dic = None
info = glob.glob('/hdfs%(inpath)s/*.info.json')
dic = json.load(open(info[0]))

script = {}
for lang in ['en','ko']:
    file = glob.glob('/hdfs%(inpath)s/*.%%s.srt' %% lang)
    if len(file) > 0:
        srt = pysrt.open(file[0])
        script[lang] = map(lambda x: {'index':x.index,'start':str(x.start.to_time()),'end':str(x.end.to_time()),'text':x.text}, srt)
dic['script'] = script

with open('/hdfs%(inpath)s/meta.json', 'w') as outfile:
    json.dump(dic, outfile)
EOF''' % locals())
        run('python2.7 gen_meta.py', quiet=True)
