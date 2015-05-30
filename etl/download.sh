#!/bin/bash
DIR=/home/ubuntu/2015/news/opengraph
DB=$DIR/joins.db
SERVER=ipc4

for i in 40
do
  SQL='select url,article from news where url like "%='$i'_____"'
  FILE=$DIR/${i}00000.txt
  ssh -i ~/.ssh/IP.pem ubuntu@$SERVER "sqlite3 -separator '' $DB '$SQL' > $FILE"
  scp -i ~/.ssh/IP.pem ubuntu@$SERVER:$FILE ./joins/
done
