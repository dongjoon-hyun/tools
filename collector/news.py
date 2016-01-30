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
News Crawler
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import time
from datetime import date
import StringIO
import sqlite3
import urllib2
import tldextract
import feedparser
from bs4 import BeautifulSoup
from twisted.protocols.ftp import FileNotFoundError
import gflags

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

FLAGS = gflags.FLAGS
gflags.DEFINE_string('crawl', None, 'Feed-list file name.', short_name='c')
gflags.DEFINE_boolean('parse', None, 'Parse.', short_name='p')
gflags.DEFINE_string('feed', None, 'Day and domain.', short_name='f')
gflags.DEFINE_boolean('debug', False, 'produces debugging output')


class News(object):
    """
    News
    """

    def __init__(self):
        pass

    @staticmethod
    def crawl(feed_list_file):
        """
        Read feed list file and call crawl_feed for each feed
        """
        with open(feed_list_file, 'r') as feeds:
            for feed in feeds.readlines():
                url = feed.split()[-1]
                News.crawl_feed(url)
                time.sleep(1)

    @staticmethod
    def crawl_feed(url):
        """
        Crawl a single feed
        """
        domain = tldextract.extract(url).domain
        day = date.today().isoformat()
        try:
            os.mkdir(day)
        except OSError:
            print "Path exists: " + day
        try:
            print url
            data = feedparser.parse(url)
        except:
            print 'Error', url
            return

        print day, domain
        with sqlite3.connect("%(day)s/%(domain)s.db" % locals()) as conn:
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS news ('
                        'ID INTEGER PRIMARY KEY AUTOINCREMENT, '
                        'url TEXT UNIQUE, '
                        'content TEXT)')
            try:
                rows = [(u'%s' % e.link,
                         u'%s' % unicode(' '.join(BeautifulSoup(e.description, "html.parser")
                                                  .get_text().split())).encode('utf8'))
                        for e in data.entries]
                cur.executemany("INSERT OR IGNORE INTO news(url,content) VALUES(?,?)", rows)
            except:
                pass
            conn.commit()

    def parse_feed(self, day_and_domain):
        """
        Parse feed.
        """
        try:
            # ex) day_and_domain = '2015-01-23_etnews'
            day = day_and_domain[:10]
            domain = day_and_domain[11:]
            db_path = "%s/%s.db" % (day, domain)
            if not os.path.isfile(db_path):
                raise FileNotFoundError
        except:
            print 'Invalid day and domain: ', db_path
            return
        print day, domain

        rows = []
        with sqlite3.connect("%(day)s/%(domain)s.db" % locals()) as conn:
            cur = conn.cursor()
            cur.execute('SELECT url FROM news')
            rows = cur.fetchall()

        for index, row in enumerate(rows, start=1):
            try:
                url = row[0]
                print '%s : (%s/%s)' % (url, index, len(rows))
                response = urllib2.urlopen(url)
                html = response.read()
                self.parse(StringIO.StringIO(html))
                time.sleep(1)
            except Exception as ex:
                print ex
        print "TOTAL: %s pages" % len(rows)

    def parse(self, ins=sys.stdin):
        """
        Parse news article with opengraph protocol
        """
        html = ''.join(ins.readlines())
        soup = BeautifulSoup(html, "html.parser")
        url = self.get_url(soup)
        domain = tldextract.extract(url).domain
        title = self.get_title(soup)
        article = self.get_article(soup)
        if FLAGS.debug:
            print domain, url
            print title
            print article
        with sqlite3.connect("%(domain)s.db" % locals()) as conn:
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS news (' +
                        'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                        'url TEXT UNIQUE, ' +
                        'title TEXT, ' +
                        'article TEXT)')
            cur.execute('INSERT OR IGNORE INTO news(url,title,article) VALUES(?,?,?)',
                        (url, title, article))
            conn.commit()

    @staticmethod
    def get_url(soup):
        """Get open-graph permanent url."""
        url = soup.find('meta', {'property': 'og:url'}).get('content')
        return url

    @staticmethod
    def get_title(soup):
        """Get title of article"""
        title = soup.find('meta', {'property': 'og:title'}).get('content')
        if title is None:
            title = soup.title.get_text()
        return title

    @staticmethod
    def is_empty(articles):
        """Check if the set of article is empty."""
        return len(articles) == 0 or len(''.join([' '.join(a.get_text().split())
                                                  for a in articles
                                                  if len(a.text.strip()) > 0])) == 0

    def get_article(self, soup):
        """Get article."""
        [s.extract() for s in soup(['script', 'iframe', 'style'])]
        articles = soup.findAll('div', {'class': 'article'})
        if self.is_empty(articles):  # joins
            articles = soup.findAll('div', {'class': 'article_content'})
        if self.is_empty(articles):  # hani
            articles = soup.findAll('div', {'class': 'article-contents'})
        if self.is_empty(articles):  # hani
            articles = soup.findAll('div', {'class': 'article-text'})
        if self.is_empty(articles):  # etnews
            articles = soup.findAll('div', {'class': 'article_body'})
        if self.is_empty(articles):  # kbs
            articles = soup.findAll('div', {'id': 'cont_newstext'})
        if self.is_empty(articles):  # mk
            articles = soup.findAll('div', {'id': 'artText'})
        if self.is_empty(articles):  # chosun
            articles = soup.findAll('div', {'id': 'news_body_id'})
        return ''.join([' '.join(a.get_text().split())
                        for a in articles
                        if len(a.text.strip()) > 0])


def main(argv):
    """Main."""
    try:
        FLAGS(argv)
    except gflags.FlagsError, ex:
        print '%s' % ex
        sys.exit(1)

    news = News()
    if FLAGS.crawl:
        news.crawl(feed_list_file=FLAGS.crawl)
    if FLAGS.parse:
        news.parse()
    if FLAGS.feed:
        news.parse_feed(day_and_domain=FLAGS.feed)

if __name__ == '__main__':
    main(sys.argv)
