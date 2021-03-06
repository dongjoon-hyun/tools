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
Public Tweet Collector
"""

# pylint: disable=line-too-long, bare-except

import io
import os
import json
import time
import datetime
import threading
import tweepy

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License 2.0'
__version__ = '0.1'


class FileOutListener(tweepy.streaming.StreamListener):
    """Standard Streaming Listener"""
    def on_data(self, status):
        try:
            status = json.loads(status)
            try:
                status_id = status['id']
                if status['lang'] != 'ko' and status['lang'] != 'en':
                    return True
                print status_id, status['created_at'], status['text']
            except:
                return True  # 'delete' tweets has no id field.
            filename = datetime.datetime.now().strftime('%Y%m%d_%H.json')
            with io.open(filename, 'a', encoding='utf-8') as jsonfile:
                jsonfile.write(unicode(json.dumps(status, ensure_ascii=False) + "\n"))
        except Exception as ex:
            print ex
        return True

    def on_error(self, status):
        print status


class S3Uploader(threading.Thread):
    """Upload into S3"""
    def run(self):
        while True:
            filename = (datetime.datetime.now() - datetime.timedelta(minutes=61)).strftime('%Y%m%d_%H.json')
            try:
                ret = os.system("aws s3 cp %s s3://mybucket/data/text/twitter/" % filename)
                if ret == 0:
                    os.remove(filename)
            except:
                pass
            time.sleep(60)


def main():
    """Main."""
    keys = open('key.txt', 'r').readlines()
    api_key = keys[0].strip()
    api_secret = keys[1].strip()
    access_token = keys[2].strip()
    access_token_secret = keys[3].strip()
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)

    uploader = S3Uploader()
    uploader.start()

    stream = tweepy.Stream(auth, FileOutListener())
    stream.sample()


if __name__ == '__main__':
    main()
