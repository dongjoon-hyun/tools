#!/bin/bash

if [ $# -eq 0 ]; then
        echo 'Command is missing.'
        exit
fi

DIR=/home/ubuntu/2015/news/opengraph
DB=$DIR/$1
SERVER=$2
i=$3
FILE=$DIR/${i}00000.txt

SQL='delete from news where url like "%='${i}'_____"'
ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "sqlite3 $DB '$SQL'"
ssh -i ~/.ssh/IP.pem ubuntu@$SERVER rm $FILE
