#!/usr/bin/env python2.7
"""
Assumption: Use general classifier to detect a user-defined class 
            representing outlier cases usually.

Input:
/data/image/voc/airplain
airplain 0.9
bus 0.07
car 0.03
...
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__ = 'Apache License'
__version__ = '0.3'

import sys

total = {}
top1 = {}
correct = {}
n = 0
false_alarm_circuit = 0
for line in sys.stdin:
    if '/' in line:
        count = 0
        ground_truth = line.split('/')[-2]
        if ground_truth in total:
            total[ground_truth] = total[ground_truth] + 1
        else:
            total[ground_truth] = 1
            correct[ground_truth] = 0
            top1[ground_truth] = 0
        #print ground_truth
        n = n + 1
    else:
        label = line.split()[0]
        if ground_truth == label:
            #print '\t', count, label, '(O)'
            if count == 0:
                top1[ground_truth] = top1[ground_truth] + 1
            correct[ground_truth] = correct[ground_truth] + 1
        else:
            #print '\t', count, label
            if label == 'circuit':
                false_alarm_circuit = false_alarm_circuit + 1
        count = count + 1

print 'Total: %d' % n
print 'Circuit: %d' % total['circuit']
print 'Correct alarm: %d' % correct['circuit']
print 'False alarm: %d' % false_alarm_circuit
print '-' * 20
print "%12s%10s%10s%10s%10s" % ('Class', 'Total', 'Top1', 'Top3', 'Miss')
for k in total.keys():
    print "%12s%10d%10d%10d%10d" % (k,total[k],top1[k],correct[k],total[k]-correct[k])
