#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Public Tweet Collector
"""

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015'
__license__   = 'Apache License 2.0'
__version__   = '0.1'

import io
import os
import sys
import tweepy
import json
import time
import datetime
import threading

class FileOutListener(tweepy.streaming.StreamListener):
    def on_data(self, status):
        try:
            s = json.loads(status)
            try:
                id = s['id']
                if s['lang'] != 'ko' and s['lang'] != 'en':
                    return True
                print s['created_at'], s['text']
            except:
                return True  # 'delete' tweets has no id field.
            file = datetime.datetime.now().strftime('%Y%m%d_%H.json')
            with io.open(file, 'a', encoding='utf-8') as f:
                f.write(unicode(json.dumps(s, ensure_ascii=False) + "\n"))
        except Exception as e:
            print e
        return True

    def on_error(self, status):
        print status

class S3Uploader(threading.Thread):
    def run(self):
        while True:
            file = (datetime.datetime.now() - datetime.timedelta(minutes=61)).strftime('%Y%m%d_%H.json')
            try:
                ret = os.system("aws s3 cp %s s3://t-ip/data/text/twitter/" % (file))
                if 0 == ret:
                    os.remove(file)
            except:
                pass
            time.sleep(60)



if __name__ == '__main__':
    f = open('key.txt', 'r')
    keys = f.readlines()
    api_key = keys[0].strip()
    api_secret = keys[1].strip()
    access_token = keys[2].strip()
    access_token_secret = keys[3].strip()
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)

    t = S3Uploader()
    t.start()

    stream = tweepy.Stream(auth, FileOutListener())
    stream.sample()
