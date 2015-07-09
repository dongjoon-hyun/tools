#!/bin/bash

if [ $# -eq 0 ]; then
        echo 'Command is missing.'
        exit
fi

DIR=/home/ubuntu/tip/etl/opengraph
if [ $1 == 'joins' ]; then
	DIR=/home/ubuntu/2015/news/opengraph
fi
DB=$DIR/$1.db
S3_PATH=s3://t-ip/data/text/news/$1/
SERVER=$2
i=$3

SQL='select url,article from news where url like "%='$i'_____"'
FILE=$DIR/${i}00000.txt
ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "sqlite3 -separator '' $DB '$SQL' > $FILE"
ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "aws s3 cp $FILE $S3_PATH"
if [ $? -eq 0 ]; then
	echo 'Done'
else
	ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "mkdir /home/ubuntu/.aws"
	scp -i ~/.ssh/IP.pem ~/.aws/* ubuntu@$SERVER:/home/ubuntu/.aws/
	ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "sudo apt-get install -y awscli"
	ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "aws s3 cp $FILE $S3_PATH"
fi
