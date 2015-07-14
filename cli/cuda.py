#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
'''
Intelligence Platform CLI Fabric File
'''

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.2'

from fabric.api import *

@task
@hosts('50.1.100.101')
def limit(gpuid,name='MAX_THREADS_PER_BLOCK'):
	'''
	fab cuda.limit:0,max_threads_per_block
	'''
	name = name.upper()
	run('''cat <<'EOF' > /home/hadoop/demo/cuda.limit.py
import pycuda.autoinit
import pycuda.driver as cuda
import pycuda.tools as tools

print cuda.Device(%(gpuid)s).pci_bus_id(),
print '\t',
print cuda.Device(%(gpuid)s).get_attribute(cuda.device_attribute.%(name)s)
EOF''' % locals())
	cmd = '/usr/local/bin/python2.7 /home/hadoop/demo/cuda.limit.py 2> /dev/null'
	run(cmd)

@task
@hosts('50.1.100.101')
def sdot(gpuid,file1,file2,outfile):
	'''
	fab cuda.sdot:0,/data/sample/m1.txt,/data/sample/m2.txt,/tmp/m3.txt
	'''
	name1 = file1.split('/')[-1]
	name2 = file2.split('/')[-1]
	run('''cat <<'EOF' > /home/hadoop/demo/cuda.sdot.py
#!/usr/local/bin/python2.7
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy as np

mod = SourceModule("""
#include <stdio.h>
__global__ void multiply_kernel(float *dest, float *a, float *b)
{
  const int i = threadIdx.x;
  dest[i] = a[i] * b[i];
}
""")
multiply_kernel = mod.get_function('multiply_kernel')

a = np.fromfile('/home/hadoop/demo/%(name1)s', dtype=np.float32, sep=' ')
b = np.fromfile('/home/hadoop/demo/%(name2)s', dtype=np.float32, sep=' ')
dest = np.zeros_like(a)
multiply_kernel(cuda.Out(dest), cuda.In(a), cuda.In(b), block=(1024,1,1), grid=(1,1))
np.savetxt('/home/hadoop/demo/cuda.tmp', dest, fmt='%%f')
EOF''' % locals())
	run('rm /home/hadoop/demo/%(file1)s 2> /dev/null' % locals())
	run('rm /home/hadoop/demo/%(file2)s 2> /dev/null' % locals())
	run('hadoop fs -get %(file1)s /home/hadoop/demo/ 2> /dev/null' % locals())
	run('hadoop fs -get %(file2)s /home/hadoop/demo/ 2> /dev/null' % locals())
	cmd = '/usr/local/bin/python2.7 /home/hadoop/demo/cuda.sdot.py 2> /dev/null'
	run(cmd)
	run('hadoop fs -put /home/hadoop/demo/cuda.tmp %(outfile)s 2> /dev/null' % locals())
