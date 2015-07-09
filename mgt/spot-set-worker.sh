#!/bin/bash
for i in `sh spot-list.sh  | grep InstanceId | awk -F\" '{print $4}'`
do
	echo "$i"
	aws ec2 create-tags --resource $i --tags "Key=Name,Value=SPOT"
done
