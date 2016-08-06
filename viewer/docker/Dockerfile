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

FROM reefrt/mesos1.0
MAINTAINER Dongjoon Hyun <dongjoon@apache.org>

COPY core-site.xml /usr/local/hadoop/etc/hadoop/
COPY rack-awareness.py /usr/local/hadoop/etc/hadoop/
COPY init-nn.sh /root/

EXPOSE 22 5050 7077 8020 8030 8031 8032 8033 8040 8042 8080 8088 10000 50010 50020 50060 50070 50075 50090
