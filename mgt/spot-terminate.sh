#!/bin/bash
for i in `sh spot-list.sh SPOT | grep InstanceId | awk -F\" '{print $4}'`
do
	echo 'Terminate ' $i 
	aws ec2 terminate-instances --instance-ids $i
done
