#!/usr/local/bin/python2.7

'''
Cluster Doctor Fabric File

Check configuration & status of all nodes in a cluster.
'''

__author__    = 'Dongjoon Hyun (dongjoon@apache.org)'
__license__   = 'Apache License'
__version__   = '0.1'

from fabric.api import *

env.roledefs = {}
nn = []
for i in range(95,99):
	nn.append('50.1.100.'+str(i))
env.roledefs['nn'] = nn
dn = []
for i in range(101,131):
	dn.append('50.1.100.'+str(i))
env.roledefs['dn'] = dn

print "\n\n", "-"*80, "\n\n# of IPs: ", len(nn + dn)

env.warn_only = True
env.skip_bad_hosts = True
env.colorize_errors = True
env.use_ssh_config = True
env.user = 'root'
env.key_filename = '~/.ssh/GPU.pem'
env.timeout = 3
env.parallel = True
output['status'] = False
output['stdout'] = True
output['warnings'] = False
output['running'] = False

@roles('nn','dn')
def os():
	'''
	OS Version: CentOS release 6.5
	'''
	cmd = "/usr/bin/lsb_release -r | cut -d '\t' -f 2"
	expected = '6.5'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def os_info():
	'''
	Display OS Version
	'''
	cmd = '/usr/bin/lsb_release -r'
	run(cmd)

@roles('nn','dn')
def kernel():
	'''
	Kernel Version: 2.6.32-431.el6.x86_64
	'''
	cmd = 'uname -r | tr -d [:space:]'
	expected = '2.6.32-431.el6.x86_64'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def selinux():
	'''
	SELINUX : disabled
	'''
	cmd = "cat /etc/sysconfig/selinux | grep 'SELINUX=disabled'"
	expected = 'SELINUX=disabled'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def sys():
	'''
	Sys Parameter: /proc/sys/kernel/hung_task_timeout_secs == 0
	'''
	cmd = 'cat /proc/sys/kernel/hung_task_timeout_secs'
	expected = '0'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

	cmd = 'grep hung_task_timeout_secs /etc/rc.local | wc -l'
	expected = '2'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def os_hugepage_enabled():
	'''
	OS Parameter: /sys/kernel/mm/redhat_transparent_hugepage/enabled == always [never]
	'''
	cmd = 'cat /sys/kernel/mm/redhat_transparent_hugepage/enabled'
	expected = 'always madvise [never]'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

	cmd = 'grep enabled /etc/rc.local | wc -l'
	expected = '2'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def os_hugepage_defrag():
	'''
	OS Parameter: cat /sys/kernel/mm/redhat_transparent_hugepage/defrag
	'''
	cmd = 'cat /sys/kernel/mm/redhat_transparent_hugepage/defrag'
	expected = 'always madvise [never]'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

	cmd = 'grep defrag /etc/rc.local | wc -l'
	expected = '2'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def date():
	'''
	System Time: time gap < 1 minute
	'''
	from datetime import datetime
	cmd = 'date +%Y-%m-%dT%H:%M'
	expected = datetime.now().isoformat()[0:16]
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def service_gmond():
	'''
	gmond Installation: chkconfig --list | grep gmond
	'''
	cmd = 'chkconfig --list|grep gmond | wc -l'
	expected = '1'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def service_gmond_on():
	'''
	gmond Running: telnet $host 8649
	'''
	cmd = 'telnet %s 8649 | grep Analysis | wc -l' % (env.host)
	expected = '1'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def disk():
	'''
	#, Usage of Disks (TODO): remaining space > 20%
	'''
	run("df -a -h | awk '{print $5}'")

@roles('nn','dn')
def disk_info():
	'''
	Display Disk Info
	'''
	cmd = "fdisk -l 2> /dev/null | grep '^Disk /dev/sd' | awk '{sum+=$3} END {print total,sum/1024}'"
	run(cmd)

	cmd = "fdisk -l 2> /dev/null | grep '^Disk /dev/sd' | awk '{print $2,$3}' | sort"
	run(cmd)

@roles('dn')
def disk_size():
	'''
	Size: /data* should be '1171964464'
	'''
	cmd = "df | grep data | awk '{print $2}' | grep -v 1171964464"
	run(cmd)

@roles('dn')
def disk_ext3():
	'''
	noatime: /data* should have 'ext3'
	'''
	run("grep '/data' /etc/fstab | grep -v ext3")

@roles('dn')
def disk_noatime():
	'''
	noatime: /data* should have 'noatime'
	'''
	run("grep '/data' /etc/fstab | grep -v noatime")

@roles('nn','dn')
def hadoop():
	'''
	Hadoop: /usr/lib/hadoop
	'''
	cmd = '[ -d /usr/lib/hadoop ] && echo 1'
	expected = '1'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('nn','dn')
def sensors():
	'''
	Sensors : Chip `Intel digital thermal sensor' (confidence: 9)
		  Chip `IPMI BMC KCS' (confidence: 8)
	'''
	cmd = "sensors | awk '{print $3}' | grep '+[6-9]'"
	run(cmd)

@roles('nn','dn')
def fan():
	'''
	Fan Speed
	'''
	cmd = "ipmi-sensors | grep Fan | grep RPM"
	run(cmd)

@roles('nn','dn')
def netstat():
	'''
	Task Tracker CLOSE_WAIT Bug Check 
	'''
	cmd = "netstat -n | grep CLOSE_WAIT | wc -l | grep '[0-9][0-9][0-9][0-9]'"
	run(cmd)

@roles('nn','dn')
def overruns():
	'''
	Network Packket Overrun Check
	'''
	cmd = "ifconfig bond0 | grep overruns | grep -v 'overruns:0'"
	run(cmd)

@roles('nn','dn')
def errors():
	'''
	Network Packket Overrun Check
	'''
	cmd = "ifconfig bond0 | grep errors | grep -v 'errors:0'"
	run(cmd)

@roles('nn','dn')
def mtu():
	'''
	Network MTU Check
	'''
	cmd = "ifconfig bond0 | grep MTU | grep -v 1500"
	run(cmd)

@roles('nn','dn')
def serial_info():
	'''
	Display Serial Number
	'''
	cmd = "dmidecode | grep 'Serial Number:' | head -n 1 | awk '{print $3}'"
	run(cmd)

@roles('nn','dn')
def model_info():
	'''
	Display HW Model Number
	'''
	cmd = "dmidecode | grep 'Product Name: ' | head -n 1 | awk '{print $3,$4,$5,$6}'"
	run(cmd)

@roles('nn','dn')
def cpu_info():
	'''
	Display CPU
	'''
	cmd = "dmidecode | grep 'CPU' | grep 'Version'"
	run(cmd)

@roles('nn','dn')
def ram_info():
	'''
	Display RAM
	'''
	cmd = "dmidecode | grep 'Size: ' | grep -v 'Range' | grep MB | awk '{print $2}' | awk '{sum+=$1} END {print sum/1024}'"
	run(cmd)

	cmd = "dmidecode | grep 'Size: ' | grep -v 'Range' | grep MB | awk '{print $2}' | wc -l"
	run(cmd)

	cmd = "dmidecode | grep 'Size: ' | grep -v 'Range' | grep MB | awk '{print $2}'"
	run(cmd)

@roles('nn','dn')
def log():
	'''
	Job Tracker & Task Tracker Log
	'''
	cmd = "df /log/hadoop 2> /dev/null | tail -n 1 | awk '{print $5}' | grep '[5-9][0-9]%'"
	run(cmd)

@roles('nn','dn')
def log_mapred():
	'''
	Non-DFS Used Data Check
	'''
	cmd = "du -s -c -h /data*/mapred/local/userlogs | tail -n 1"
	run(cmd)

@roles('nn','dn')
def height():
	'''
	Height
	'''
	cmd = "dmidecode | grep Height | awk '{print $2}'"
	run(cmd)

@roles('nn','dn')
def uptime():
	'''
	Uptime
	'''
	cmd = "uptime"
	run(cmd)

@roles('nn','dn')
def hostname():
	'''
	Hostname
	'''
	cmd = "hostname"
	run(cmd)

@roles('dn')
def gpu():
	'''
	GPU: 84:00.0 3D controller: NVIDIA Corporation GK210GL [Tesla K80] (rev a1)
	'''
	cmd = "lspci | grep -i nvidia | tr -d '[:space:]'"
	expected = '84:00.03Dcontroller:NVIDIACorporationGK210GL[TeslaK80](reva1)' + '85:00.03Dcontroller:NVIDIACorporationGK210GL[TeslaK80](reva1)'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('dn')
def gpu_uuid_info():
	'''
	GPU UUID
	'''
	cmd = "nvidia-smi -L"
	run(cmd)

@roles('dn')
def r():
	'''
	R Version: R version 3.1.3 (2015-03-09) -- "Smooth Sidewalk"
	'''
	cmd = "/usr/bin/R --version | head -n 1 | cut -d ' ' -f 3"
	expected = '3.1.3'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

@roles('dn')
def sge_execd():
	'''
	Sun Grid Engine Daemon
	'''
	cmd = "ps aux | grep sge_execd | grep hmi | wc -l"
	expected = '1'
	run('''[ "`%(cmd)s`" != "%(expected)s" ] && (echo "Expected: %(expected)s, Actual: `%(cmd)s`")''' % locals())

