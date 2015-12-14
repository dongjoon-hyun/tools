#!/bin/bash
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
