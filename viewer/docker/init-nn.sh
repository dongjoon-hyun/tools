#!/bin/bash

/usr/sbin/sshd

hostname > /usr/etc/mesos/masters
grep hdn /etc/hosts | awk '{print $1}' | sort | uniq > $HADOOP_PREFIX/etc/hadoop/slaves
cp $HADOOP_PREFIX/etc/hadoop/slaves /usr/etc/mesos/slaves
for host in `cat $HADOOP_PREFIX/etc/hadoop/slaves`
do
    scp /etc/hosts $host:/etc/hosts
    scp $HADOOP_PREFIX/etc/hadoop/slaves $host:$HADOOP_PREFIX/etc/hadoop/slaves
    scp /usr/etc/mesos/masters $host:/usr/etc/mesos/masters
    scp /usr/etc/mesos/slaves $host:/usr/etc/mesos/slaves
    ssh $host mesos-daemon.sh mesos-slave --master=hnn-001-01:5050
done

/usr/local/hadoop/bin/hdfs namenode -format
/usr/local/hadoop/sbin/start-dfs.sh
/usr/local/hadoop/sbin/start-yarn.sh
mesos-daemon.sh mesos-master --cluster=REEF --work_dir=/var/lib/mesos --log_dir=/var/log/mesos

cd ~ && /bin/bash
