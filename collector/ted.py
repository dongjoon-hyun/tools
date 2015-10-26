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
TED Crawler
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015'
__license__ = 'Apache License'
__version__ = '0.1'

import os
import re
import sys
import time
import getopt
import urllib2
from bs4 import BeautifulSoup


class TED:
    """
    TED
    """

    def __init__(self):
        pass

    def crawl(self, lang='ko'):
        try:
            os.mkdir('talks')
        except:
            pass
        for page in range(1, 50):
            for language in [lang]:
                url = 'http://www.ted.com/talks?language=%(language)s&page=%(page)s&sort=newest' % locals()
                self.crawl_page(url, language)

    def crawl_page(self, url, language):
        print url
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        for link in soup.find_all('a'):
            url = link.get('href')
            if url.startswith('/talks/'):
                filename = url.split('?')[0]
                if os.path.isfile('.%(filename)s_%(language)s.html' % locals()):
                    continue
                html_file = open('.%(filename)s_%(language)s.html' % locals(), 'w')
                print 'http://www.ted.com%(filename)s?language=%(language)s' % locals()
                f = urllib2.urlopen('http://www.ted.com%(filename)s/transcript?language=%(language)s' % locals())
                html_file.write(f.read())
                html_file.close()

                en_html_file = open('.%(filename)s_en.html' % locals(), 'w')
                print 'http://www.ted.com%(filename)s?language=en' % locals()
                en_f = urllib2.urlopen('http://www.ted.com%(filename)s/transcript?language=en' % locals())
                en_html_file.write(en_f.read())
                en_html_file.close()

                detail_html_file = open('.%(filename)s_detail.html' % locals(), 'w')
                print 'http://www.ted.com%(filename)s' % locals()
                detail_f = urllib2.urlopen('http://www.ted.com%(filename)s' % locals())
                content = detail_f.read()
                detail_html_file.write(content)
                detail_html_file.close()
                video_url = re.search('(http://download.ted.com/talks/[^"]+)', ''.join(content)).group(0)
                self.crawl_video(video_url, ".%(filename)s.mp4" % locals())
                time.sleep(3)

    @staticmethod
    def crawl_video(url, filename):
        print 'Download', url
        os.system('curl -o %(filename)s -LO %(url)s' % locals())

    @staticmethod
    def parse():
        for root, dirs, files in os.walk("talks"):
            for name in files:
                if name.endswith('txt') or name.endswith('detail'):
                    continue
                print name
                soup = BeautifulSoup(open('talks/' + name,'r'))
                subtitle_file = open('talks/%(name)s_txt' % locals(), 'w')
                for script in soup.find_all('span', 'talk-transcript__fragment'):
                    subtitle_file.write(unicode(script.text).encode('utf8'))
                subtitle_file.close()


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcp", ["help", "crawl", "parse"])
    except getopt.GetoptError as err:
        sys.exit(0)

    ted = TED()
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            sys.exit()
        elif o in ("-c", '--crawl'):
            ted.crawl()
        elif o in ("-p", '--parse'):
            ted.parse()
