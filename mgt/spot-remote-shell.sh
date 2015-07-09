#!/bin/bash
region=ap-northeast-1
aws_access_key_id=AKIAJ6CPMBODIHTVGSKQ
aws_secret_access_key=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

for h in `sh spot-list.sh SPOT | grep PublicIpAddress | awk -F\" '{print $4}'`
do
	ssh -i ~/.ssh/IP.pem -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$h "AWS_ACCESS_KEY_ID=$aws_access_key_id AWS_SECRET_ACCESS_KEY=$aws_secret_access_key AWS_DEFAULT_REGION=$region $@"
done
