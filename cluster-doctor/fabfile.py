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
Cluster Doctor Fabric File
Check configuration & status of all nodes in a cluster.
"""

__author__ = 'Dongjoon Hyun (dongjoon@apache.org)'
__copyright__ = 'Copyright (c) 2015'
__license__ = 'Apache License'
__version__ = '0.1'

from fabric.api import *

env.roledefs = dict()
env.roledefs['nn'] = []  # Add name node IPs
env.roledefs['dn'] = []  # Add data node IPs

print "\n\n", "-" * 80, "\n\n# of IPs: ", len(env.roledefs['nn'] + env.roledefs['dn'])

env.warn_only = True
env.skip_bad_hosts = True
env.colorize_errors = True
env.use_ssh_config = True
env.user = 'root'
env.key_filename = ''  # Add a keyfile
env.timeout = 3
env.parallel = True
output['status'] = False
output['stdout'] = True
output['warnings'] = False
output['running'] = False


@roles('nn', 'dn')
def os():
    """
    OS Version: CentOS release 6.7
    """
    cmd = "/usr/bin/lsb_release -r | cut -d '\t' -f 2"
    expected = '6.7'
    run("""[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")""" % locals())


@roles('nn', 'dn')
def os_info():
    """
    Display OS Version
    """
    cmd = '/usr/bin/lsb_release -r'
    run(cmd)


@roles('nn', 'dn')
def kernel():
    """
    Kernel Version: XXX
    """
    cmd = 'uname -r | tr -d [:space:]'
    expected = 'XXX'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def selinux():
    """
    SELINUX : disabled
    """
    cmd = "cat /etc/sysconfig/selinux | grep 'SELINUX=disabled'"
    expected = 'SELINUX=disabled'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def sys():
    """
    Sys Parameter: /proc/sys/kernel/hung_task_timeout_secs == 0
    """
    cmd = 'cat /proc/sys/kernel/hung_task_timeout_secs'
    expected = '0'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

    cmd = 'grep hung_task_timeout_secs /etc/rc.local | wc -l'
    expected = '2'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def os_hugepage_enabled():
    """
    OS Parameter: /sys/kernel/mm/redhat_transparent_hugepage/enabled == always [never]
    """
    cmd = 'cat /sys/kernel/mm/redhat_transparent_hugepage/enabled'
    expected = 'always madvise [never]'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

    cmd = 'grep enabled /etc/rc.local | wc -l'
    expected = '2'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def os_hugepage_defrag():
    """
    OS Parameter: cat /sys/kernel/mm/redhat_transparent_hugepage/defrag
    """
    cmd = 'cat /sys/kernel/mm/redhat_transparent_hugepage/defrag'
    expected = 'always madvise [never]'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

    cmd = 'grep defrag /etc/rc.local | wc -l'
    expected = '2'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def date():
    """
    System Time: time gap < 1 minute
    """
    from datetime import datetime
    cmd = 'date +%Y-%m-%dT%H:%M'
    expected = datetime.now().isoformat()[0:16]
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def service_gmond():
    """
    gmond Installation: chkconfig --list | grep gmond
    """
    cmd = 'chkconfig --list|grep gmond | wc -l'
    expected = '1'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def service_gmond_on():
    """
    gmond Running: telnet $host 8649
    """
    cmd = 'telnet %s 8649 | grep Analysis | wc -l' % (env.host)
    expected = '1'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def disk():
    """
    #, Usage of Disks (TODO): remaining space > 20%
    """
    run("df -a -h | awk '{print $5}'")


@roles('nn', 'dn')
def disk_info():
    """
    Display Disk Info
    """
    cmd = "fdisk -l 2> /dev/null | grep '^Disk /dev/sd' | awk '{sum+=$3} END {print total,sum/1024}'"
    run(cmd)

    cmd = "fdisk -l 2> /dev/null | grep '^Disk /dev/sd' | awk '{print $2,$3}' | sort"
    run(cmd)


@roles('dn')
def disk_size():
    """
    Size: /data* should be 'xxxxxx'
    """
    cmd = "df | grep data | awk '{print $2}' | grep -v xxxxxx"
    run(cmd)


@roles('dn')
def disk_ext4():
    """
    noatime: /data* should have 'ext4'
    """
    run("grep '/data' /etc/fstab | grep -v ext4")


@roles('dn')
def disk_noatime():
    """
    noatime: /data* should have 'noatime'
    """
    run("grep '/data' /etc/fstab | grep -v noatime")


@roles('nn', 'dn')
def hadoop():
    """
    Hadoop: /usr/lib/hadoop
    """
    cmd = '[ -d /usr/lib/hadoop ] && echo 1'
    expected = '1'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('nn', 'dn')
def sensors():
    """
    Sensors : Chip `Intel digital thermal sensor' (confidence: 9)
          Chip `IPMI BMC KCS' (confidence: 8)
    """
    cmd = "sensors | awk '{print $3}' | grep '+[0-9]' | sort -r | head -1"
    run(cmd)


@roles('nn', 'dn')
def fan():
    """
    Fan Speed
    """
    cmd = "ipmi-sensors | grep Fan | grep RPM | awk -F '|' '{print $4}' | sort -r | head -1"
    run(cmd)


@roles('nn', 'dn')
def netstat():
    """
    Task Tracker CLOSE_WAIT Bug Check 
    """
    cmd = "netstat -n | grep CLOSE_WAIT | wc -l | grep '[0-9][0-9][0-9][0-9]'"
    run(cmd)


@roles('nn', 'dn')
def overruns():
    """
    Network Packet Overrun Check
    """
    cmd = "ifconfig bond0 | grep overruns | grep -v 'overruns:0'"
    run(cmd)


@roles('nn', 'dn')
def errors():
    """
    Network Packet Overrun Check
    """
    cmd = "ifconfig bond0 | grep errors | grep -v 'errors:0'"
    run(cmd)


@roles('nn', 'dn')
def mtu():
    """
    Network MTU Check
    """
    cmd = "ifconfig bond0 | grep MTU | grep -v 1500"
    run(cmd)


@roles('nn', 'dn')
def serial_info():
    """
    Display Serial Number
    """
    cmd = "dmidecode | grep 'Serial Number:' | head -n 1 | awk '{print $3}'"
    run(cmd)


@roles('nn', 'dn')
def model_info():
    """
    Display HW Model Number
    """
    cmd = "dmidecode | grep 'Product Name: ' | head -n 1 | awk '{print $3,$4,$5,$6}'"
    run(cmd)


@roles('nn', 'dn')
def cpu_info():
    """
    Display CPU
    """
    cmd = "dmidecode | grep 'CPU' | grep 'Version'"
    run(cmd)


@roles('nn', 'dn')
def ram_info():
    """
    Display RAM
    """
    cmd = "dmidecode | grep 'Size: ' | grep -v 'Range' | grep MB | awk '{print $2}' | \
awk '{sum+=$1} END {print sum/1024}'"
    run(cmd)

    cmd = "dmidecode | grep 'Size: ' | grep -v 'Range' | grep MB | awk '{print $2}' | wc -l"
    run(cmd)

    cmd = "dmidecode | grep 'Size: ' | grep -v 'Range' | grep MB | awk '{print $2}'"
    run(cmd)


@roles('nn', 'dn')
def height():
    """
    Height
    """
    cmd = "dmidecode | grep Height | awk '{print $2}'"
    run(cmd)


@roles('nn', 'dn')
def uptime():
    """
    Uptime
    """
    cmd = "uptime"
    run(cmd)


@roles('nn', 'dn')
def hostname():
    """
    Hostname
    """
    cmd = "hostname"
    run(cmd)


@roles('dn')
def gpu():
    """
    GPU: 84:00.0 3D controller: NVIDIA Corporation GK210GL [Tesla K80] (rev a1)
    """
    cmd = "lspci | grep -i nvidia | tr -d '[:space:]'"
    expected = '84:00.03Dcontroller:NVIDIACorporationGK210GL[TeslaK80](reva1)' + \
               '85:00.03Dcontroller:NVIDIACorporationGK210GL[TeslaK80](reva1)'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('dn')
def gpu_uuid_info():
    """
    GPU UUID
    """
    cmd = "nvidia-smi -L"
    run(cmd)


@roles('dn')
def r():
    """
    R version 3.2.2 (2015-08-14) -- "Fire Safety"
    """
    cmd = "/usr/bin/R --version | head -n 1 | cut -d ' ' -f 3"
    expected = '3.2.2'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('dn')
def sge_execd():
    """
    Sun Grid Engine Daemon
    """
    cmd = "ps aux | grep sge_execd | grep hmi | wc -l"
    expected = '1'
    run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())


@roles('dn')
def hdfs_mount():
    """
    Check /hdfs/ mounting
    """
    cmd = "ls /hdfs"
    run(cmd)


@roles('nn', 'dn')
def alive():
    """
    Check server are alive
    """
    cmd = "echo alive"
    run(cmd)


@roles('dn')
def gpu_temp():
    """
    GPU Temperature
    """
    cmd = "nvidia-smi -q -d TEMPERATURE | grep 'GPU Current Temp'"
    run(cmd)


@roles('dn')
def gpu_usage():
    """
    GPU Usage
    """
    cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv | tail -2"
    run(cmd)
