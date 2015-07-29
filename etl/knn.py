#!/usr/bin/env python
# coding: utf-8
"""
News Categorization
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'

import os
import sys
import codecs
import heapq
import datetime
import collections

reload(sys)
sys.setdefaultencoding('utf8')
import feedparser


def jaccard_dist(a, b):
    s1, s2 = set(a), set(b)
    all = s1.union(s2)
    if len(all) == 0:
        return 0
    return 1 - 1.0 * len(s1.intersection(s2)) / len(all)


def bagofwords(a, b):
    c1 = collections.Counter(a)
    c2 = collections.Counter(b)
    total, inter = 0, 0
    for (k, c) in c1.most_common():
        total = total + c
        if k in c2:
            inter = inter + c
    for (k, c) in c2.most_common():
        if k not in c1:
            total = total + c
    return 1 - 1.0 * inter / total


def cleansing(s):
    chars = [u'N' if c.isdigit() else c for c in s]
    chars = [u'퍼센트' if c == u'%' else c for c in chars]
    chars = [c for c in chars if c == u'N' or (u'가' <= c <= u'힣')]
    return ''.join(chars)


def ngram(s, n=2):
    chars = [c for c in s]
    result = []
    for i in xrange(len(chars) - n + 1):
        result.append(''.join(chars[i:i + n]))
    return result


class News:
    dic = {
        "경제": range(101, 109),
        "건설/부동산": range(301, 308),
        "건강": range(1001, 1008),
        "교육": range(1101, 1109),
        "금융": range(201, 207),
        "기술": range(601, 614),
        "농수산": range(1701, 1705),
        "라이프": range(901, 910),
        "레저": range(1301, 1307),
        "문화/연예": range(1201, 1211),
        "물류/교통": range(1801, 1806),
        "미디어": range(701, 707),
        "사회": range(1901, 1909),
        "산업": range(401, 409),
        "스포츠": range(1601, 1611),
        "에너지/환경": range(1501, 1506),
        "유통": range(801, 809),
        "자동차": range(501, 508),
        "정부/정책": range(1401, 1409)
    }

    dic1, dic2 = {}, {}

    def download(self):
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        with codecs.open(filename + '.txt', 'w', encoding='utf8') as f:
            for cat1, ids in self.dic.iteritems():
                for id in ids:
                    url = 'http://api.newswire.co.kr/rss/industry/%(id)s' % locals()
                    d = feedparser.parse(url)
                    for i in d['entries']:
                        cat2 = i['tags'][0]['term']
                        title = i['title'] + ' '.join(i['description'].split())
                        print >> f, "%(cat1)s\t%(cat2)s\t%(title)s" % locals()

    def read_data(self):
        dic1, dic2 = {}, {}
        for file in [f for f in os.listdir('.') if '.txt' in f]:
            print file
            with codecs.open(file, 'r', encoding='utf8') as f:
                for line in f.readlines():
                    parts = line.split()
                    cat1, cat2, title = parts[0], parts[1], cleansing(''.join(parts[3:]))
                    words = ngram(title, 2) + ngram(title, 3) + ngram(title, 4)
                    if cat1 in dic2:
                        if cat2 in dic2[cat1]:
                            dic2[cat1][cat2] = dic2[cat1][cat2] + words
                        else:
                            dic2[cat1][cat2] = words
                    else:
                        dic2[cat1] = {cat2: words}
        for cat1 in dic2.keys():
            v = []
            for cat2 in dic2[cat1].keys():
                v = v + dic2[cat1][cat2]
            dic1[cat1] = v
        self.dic1, self.dic2 = dic1, dic2

    def knn(self, new_data):
        new_data = cleansing(new_data)
        new_words = ngram(new_data, 2) + ngram(new_data, 3) + ngram(new_data, 4)

        h = []
        for cat1 in self.dic1.keys():
            heapq.heappush(h, (bagofwords(self.dic1[cat1], new_words), cat1))
        d, c = heapq.heappop(h)

        h = []
        for cat1 in self.dic2.keys():
            for cat2 in self.dic2[cat1].keys():
                heapq.heappush(h, (bagofwords(self.dic2[cat1][cat2], new_words), (cat1, cat2)))
        while True:
            d, (c1, c2) = heapq.heappop(h)
            if c == c1:
                break
        return c1, c2


if __name__ == '__main__':
    News().download()
    pass
