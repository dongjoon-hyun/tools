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
CUDA CLI Fabric File
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015-2016'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import *


@task
@hosts('50.1.100.101')
def show():
    """
    fab cuda.show
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        run('''cat <<'EOF' > cuda.show.py
import pycuda.driver as cuda

cuda.init()
print "%%d device(s) found." %% cuda.Device.count()
for ordinal in range(cuda.Device.count()):
    dev = cuda.Device(ordinal)
    print "Device #%%d: %%s" %% (ordinal, dev.name())
    print " Compute Capability: %%d.%%d" %% dev.compute_capability()
    print " Total Memory: %%s GB" %% (dev.total_memory()//(1024*1024*1024))
EOF''' % locals())
        cmd = '/usr/local/bin/python2.7 cuda.show.py 2> /dev/null'
        run(cmd)


@task
@hosts('50.1.100.101')
def limit(gpuid, name='MAX_THREADS_PER_BLOCK'):
    """
    fab cuda.limit:0,max_threads_per_block
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        name = name.upper()
        run('''cat <<'EOF' > cuda.limit.py
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
def sdot(gpuid, file1, file2, outfile):
    """
    fab cuda.sdot:0,/sample/m1.txt,/sample/m2.txt,/tmp/m3.txt
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        name1 = file1.split('/')[-1]
        name2 = file2.split('/')[-1]
        run('''cat <<'EOF' > cuda.sdot.py
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy as np

mod = SourceModule("""
__global__ void multiply_kernel(float *dest, float *a, float *b)
{
  const int i = threadIdx.x;
  dest[i] = a[i] * b[i];
}
""")
multiply_kernel = mod.get_function('multiply_kernel')

a = np.fromfile('%(name1)s', dtype=np.float32, sep=' ')
b = np.fromfile('%(name2)s', dtype=np.float32, sep=' ')
dest = np.zeros_like(a)
multiply_kernel(cuda.Out(dest), cuda.In(a), cuda.In(b), block=(1024,1,1), grid=(1,1))
np.savetxt('cuda.tmp', dest, fmt='%%f')
EOF''' % locals())
        run('hadoop fs -get %(file1)s 2> /dev/null' % locals())
        run('hadoop fs -get %(file2)s 2> /dev/null' % locals())
        cmd = '/usr/local/bin/python2.7 cuda.sdot.py 2> /dev/null'
        run(cmd)
        run('hadoop fs -put cuda.tmp %(outfile)s 2> /dev/null' % locals())


# working
def sgemm_c(gpuid, file1, file2, outfile):
    """
    fab cuda.sgemm:0,/sample/m1.txt,/sample/m2.txt,/tmp/m3.txt
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        name1 = file1.split('/')[-1]
        name2 = file2.split('/')[-1]
        run('''cat <<'EOF' > cuda.sgemm.py
import pycuda.autoinit
import pycuda.gpuarray as gpuarray
import pycuda.driver as cuda
import numpy as np

import skcuda.linalg as culinalg
import skcuda.misc as cumisc
culinalg.init()

a = np.fromfile('%(name1)s', dtype=np.float32, sep=' ')
b = np.fromfile('%(name2)s', dtype=np.float32, sep=' ')
c = np.zeros_like(a)

a_gpu = gpuarray.to_gpu(a)
b_gpu = gpuarray.to_gpu(b)
c_gpu = culinalg.dot(a_gpu, c_gpu)
print c_gpu
EOF''' % locals())
        run('hadoop fs -get %(file1)s 2> /dev/null' % locals())
        run('hadoop fs -get %(file2)s 2> /dev/null' % locals())
        cmd = '/usr/local/bin/python2.7 cuda.sgemm.py 2> /dev/null'
        run(cmd)
        run('hadoop fs -put cuda.tmp %(outfile)s 2> /dev/null' % locals())


# working
def sgemm_(gpuid, file1, file2, outfile):
    """
    fab cuda.sgemm:0,/sample/m1.txt,/sample/m2.txt,/tmp/m3.txt
    """
    run('mkdir %s' % env.dir)
    with cd(env.dir):
        name1 = file1.split('/')[-1]
        name2 = file2.split('/')[-1]
        run('''cat <<'EOF' > cuda.sgemm.py
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy as np

mod = SourceModule("""
#define INDX( row, col, ld ) ( ( (col) * (ld) ) + (row) )
__global__ void sgemm_kernel(int m, int n, int k, float *a, float *b, float *c) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    int j = blockIdx.y * blockDim.y + threadIdx.y;
    float tmp = 0.0;
    for( int koff = 0; koff < k; koff++ )
        tmp += a[INDX(i, koff, m)] * b[INDX(koff, j, n)];
    c[INDX(i, j, m)] = tmp;
}
""")
sgemm_kernel = mod.get_function('sgemm_kernel')

a = np.fromfile('%(name1)s', dtype=np.float32, sep=' ')
b = np.fromfile('%(name2)s', dtype=np.float32, sep=' ')
dest = np.zeros_like(a)

block_size = 32
grid_size = 1
# 2d picture - map to 2d grid
grid = (grid_size,grid_size)
block = (block_size,block_size,1)
size = block_size * grid_size

sgemm_kernel(np.int32(32),np.int32(32),np.int32(32),cuda.Out(dest), cuda.In(a), cuda.In(b), block=block, grid=grid)
print dest
np.savetxt('cuda.tmp', dest, fmt='%%f')
EOF''' % locals())
        run('hadoop fs -get %(file1)s 2> /dev/null' % locals())
        run('hadoop fs -get %(file2)s 2> /dev/null' % locals())
        cmd = '/usr/local/bin/python2.7 cuda.sgemm.py 2> /dev/null'
        run(cmd)
        run('hadoop fs -put cuda.tmp %(outfile)s 2> /dev/null' % locals())
