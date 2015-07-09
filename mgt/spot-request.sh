#!/bin/bash

aws ec2 request-spot-instances \
--availability-zone-group ap-northeast-1a \
--spot-price 0.015 \
--instance-count 1 \
--type "one-time" \
--launch-specification \
"{
    \"ImageId\":\"ami-64a16764\", \
    \"InstanceType\":\"m3.medium\", \
    \"KeyName\":\"IP\", \
    \"SecurityGroups\": [\"IP\"], \
    \"UserData\":\"`base64 userdata.sh`\" \
}"
