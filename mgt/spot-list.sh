#!/bin/bash

if [ $# -eq 0 ]; then
	FILETER=
else
	FILETER="Name=tag-value,Values=$@"
fi

aws ec2 describe-instances --filter "Name=instance-lifecycle,Values=spot" "Name=instance-state-name,Values=running" $FILTER
