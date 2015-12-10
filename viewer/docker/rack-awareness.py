#!/usr/bin/env python
#-*-coding:UTF-8 -*-  

import sys

rack = {
    "172.17.0.2":"rack1",
    "172.17.0.3":"rack1",
    "172.17.0.4":"rack2",
}

if __name__=="__main__":
    print "/" + rack.get(sys.argv[1],"default-rack"),
