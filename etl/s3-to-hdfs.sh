#!/bin/bash
if [ $# -eq 0 ]; then
        echo 'Target is missing.'
        exit
fi
DIR=$(dirname $1)/$(basename $1)
for f in `/usr/local/bin/aws s3 ls s3://t-ip$DIR/ | awk '{print $4}'`;
do
	if [ ! -f /hdfs$DIR/$f ]; then
		echo $f
		/usr/local/bin/aws s3 cp s3://t-ip$DIR/$f /tmp/
		cp /tmp/$f /hdfs$DIR/
		rm /tmp/$f
	fi
done
