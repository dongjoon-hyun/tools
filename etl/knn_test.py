#!/usr/bin/env python
# coding: utf-8
"""
News Catagorization
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'

import unittest
import a


class TestStringMethods(unittest.TestCase):
    def test_dist(self):
        self.assertEqual(a.jaccard_dist([1], [1]), 0)
        self.assertEqual(a.jaccard_dist([1], [2]), 1)
        self.assertAlmostEqual(a.jaccard_dist([1, 2], [2, 3]), 2.0 / 3.0)

    def test_ngram(self):
        self.assertEqual([], a.ngram(u'한', 2))
        self.assertEqual([u'한글'], a.ngram(u'한글', 2))
        self.assertEqual([u'대한', u'한민', u'민국'], a.ngram(u'대한민국', 2))
        self.assertEqual([u'대한민', u'한민국'], a.ngram(u'대한민국', 3))

    def test_knn(self):
        news = a.News()
        news.read_data()
        self.assertEqual((u'건강', u'병원/의료'), news.knn(u"허술한 방역·부실한 대응…'의료선진국' 정부 민낯 드러나"))
        self.assertEqual((u'정부/정책', u'정당/국회'), news.knn(u"대통령 국정 긍정평가 한 달여 전과 비슷한 40% 중반 대"))
        self.assertEqual((u'정부/정책', u'외교/통일'), news.knn(u"김무성 '워싱턴 외교' 마무리…'한미동맹' 강조"))
        self.assertEqual((u'산업', u'조선'), news.knn(u"대우조선해양, 빅데이터 활용해 조선산업 경쟁력 강화 추진"))
        self.assertEqual((u'금융', u'증권'), news.knn(u"KDB대우증권, ELS 8종 DLS 3종 DLB 1종 공모"))
        self.assertEqual((u'금융', u'증권'), news.knn(u"코스닥지수가 2% 가까이 떨어졌다. 730선을 간신히 지켰다"))
        self.assertEqual((u'자동차', u'승용차'), news.knn(u"닛산·볼보·크라이슬러 6,708대 리콜 실시"))
        self.assertEqual((u'사회', u'재난/안전'), news.knn(u"경기도, 화재·교통사고에서 가장 안전한 지자체로 선정"))
        self.assertEqual((u'스포츠', u'골프'), news.knn(u"건국대 이보미, 일본 JLPGA투어 시즌 3승…리코컵 우승"))
        self.assertEqual((u'에너지/환경', u'신재생에너지'), news.knn(u"서울시 최대 태양광 발전소 강북아리수정수센터 본격 가동"))


if __name__ == '__main__':
    unittest.main()
