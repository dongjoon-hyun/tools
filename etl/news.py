#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
News Feed Crawler
'''
from twisted.protocols.ftp import FileNotFoundError

__author__    = 'Dongjoon Hyun'
__copyright__ = 'Copyright (c) 2015'
__license__   = 'Apache License 2.0'
__version__   = '0.1'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import time
from datetime import date
import getopt
import sqlite3
import urllib2
import tldextract
import feedparser
from bs4 import BeautifulSoup
import StringIO

class News:
	'''News'''

	def __init__(self):
		pass

	def crawl(self, feed_list_file, verbose=False):
		'''Read feed list file and call crawl_feed for each feed'''
		f = open(feed_list_file,'r')
		feeds = f.readlines()
		f.close()	
		for feed in feeds:
			url = feed.split()[-1]
			self.crawl_feed(url, verbose)
			time.sleep(1)

	def crawl_feed(self, url, verbose):
		'''Crawl a single feed'''
		domain = tldextract.extract(url).domain
		day = date.today().isoformat()
		try:
			os.mkdir(day)
		except:
			pass
		try:
			print url
			d = feedparser.parse(url)
		except:
			print 'Error', url
			return
			
		with sqlite3.connect("%(day)s/%(domain)s.db" % locals()) as conn:
			c = conn.cursor()
			c.execute('CREATE TABLE IF NOT EXISTS news (ID INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, content TEXT)')
			try:
				rows = [(u'%s' % e.link, u'%s' % unicode(' '.join(BeautifulSoup(e.description).get_text().split())).encode('utf8')) for e in d.entries]
				c.executemany("INSERT OR IGNORE INTO news(url,content) VALUES(?,?)", rows)
			except:
				pass
			conn.commit()
			
	def parse_feed(self, day_and_domain, verbose=False):
		try:
			# ex) day_and_domain = '2015-01-23_etnews'
			day = day_and_domain[:10]
			domain = day_and_domain[11:]
			db_path = "%s/%s.db" % (day, domain)
			if os.path.isfile(db_path) == False:
				raise FileNotFoundError
				
		except:
			print 'Invalid day and domain: ', db_path
			return
		
		print day, domain
		
		rows = []
		with sqlite3.connect("%(day)s/%(domain)s.db" % locals()) as conn:
			c = conn.cursor()
			c.execute('SELECT url FROM news')
			rows = c.fetchall()
			
		for index, row in enumerate(rows, start=1):
			try:
				url = row[0]
				print '%s : (%s/%s)' % (url, index, len(rows))
				response = urllib2.urlopen(url)
				html = response.read()
				self.parse(StringIO.StringIO(html), verbose)
				time.sleep(1)
			except Exception as e:
				print e
				pass
		print "TOTAL: %s pages" % len(rows)

	def parse(self, input=sys.stdin, verbose=False):
		'''Parse news article with opengraph protocol'''
		html = ''.join(input.readlines())
		soup = BeautifulSoup(html)
		url = self.get_url(soup)
		domain = tldextract.extract(url).domain
		title = self.get_title(soup)
		article = self.get_article(soup)
		if verbose:
			print url
			print title
			print article
		with sqlite3.connect("opengraph/%(domain)s.db" % locals()) as conn:
			c = conn.cursor()
			c.execute('CREATE TABLE IF NOT EXISTS news (ID INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, title TEXT, article TEXT)')
			c.execute('INSERT OR IGNORE INTO news(url,title,article) VALUES(?,?,?)', (url, title, article))
			conn.commit()
		
	def get_url(self, soup):
		url = soup.find('meta', {'property': 'og:url'}).get('content')
		return url

	def get_title(self, soup):
		title = soup.find('meta', {'property': 'og:title'}).get('content')
		if None == title:
			title = soup.title.get_text()
		return title
		
	def get_article(self, soup):
		[s.extract() for s in soup(['script','iframe','style'])]
		articles = soup.findAll('div', {'class': 'article'})
		if self.is_empty(articles): # joins
			articles = soup.findAll('div', {'class': 'article_content'})
		if self.is_empty(articles): # hani
			articles = soup.findAll('div', {'class': 'article-contents'})
		if self.is_empty(articles): # hani
			articles = soup.findAll('div', {'class': 'article-text'})
		if self.is_empty(articles): # etnews
			articles = soup.findAll('div', {'class': 'article_body'})
		if self.is_empty(articles): # kbs
			articles = soup.findAll('div', {'id': 'cont_newstext'})
		if self.is_empty(articles): # mk
			articles = soup.findAll('div', {'id': 'artText'})
		if self.is_empty(articles): # chosun
			articles = soup.findAll('div', {'id': 'news_body_id'})
		return ''.join([' '.join(a.get_text().split()) for a in articles if len(a.text.strip())>0])

	def is_empty(self, articles):
		return 0 == len(articles) or 0 == len(''.join([' '.join(a.get_text().split()) for a in articles if len(a.text.strip())>0]))

	
if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hvc:pf:", ["help", "crawl", "parse", "feed"])
	except getopt.GetoptError as err:
		sys.exit(0)

	news = News()
	verbose = False
	for o, a in opts:
		if o in ("-h", "--help"):
			sys.exit()
		elif o == "-v":
			verbose = True

	for o, a in opts:
		if o in ("-c", '--crawl'):
			news.crawl(feed_list_file=a, verbose=verbose)
		elif o in ("-p", '--parse'):
			news.parse(verbose=verbose)
		elif o in ("-f", '--feed'):
			news.parse_feed(day_and_domain=a, verbose=verbose)
