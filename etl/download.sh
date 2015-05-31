#!/bin/bash

if [ $# -eq 0 ]; then
        echo 'Command is missing.'
        exit
fi

DIR=/home/ubuntu/2015/news/opengraph
DB=$DIR/$1
SERVER=$2
i=$3

SQL='select url,article from news where url like "%='$i'_____"'
FILE=$DIR/${i}00000.txt
ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "sqlite3 -separator '' $DB '$SQL' > $FILE"
scp -i ~/.ssh/IP.pem ubuntu@$SERVER:$FILE ./joins/
