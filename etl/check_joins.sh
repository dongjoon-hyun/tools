#!/usr/local/bin/bash

date
for h in ipc1 ipc2 ipc3 ipc4 ipc5 ipc6 ipc-api
do
	ssh -i ~/.ssh/IP.pem ubuntu@$h "sqlite3 /home/ubuntu/2015/news/opengraph/joins.db 'select url,substr(article,0,10) from news order by id limit 1'"
	ssh -i ~/.ssh/IP.pem ubuntu@$h "sqlite3 /home/ubuntu/2015/news/opengraph/joins.db 'select url,substr(article,0,10) from news order by id desc limit 1'"
done
