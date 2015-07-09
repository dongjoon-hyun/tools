#!/bin/bash

# Initialize
sudo apt-get install -y awscli

# Register myself as a worker
aws sqs send-message --queue-url https://ap-northeast-1.queue.amazonaws.com/782748997589/WORKER --message-body `curl http://169.254.169.254/latest/meta-data/public-ipv4`

# Upload result
#aws s3 cp 590000.txt s3://t-ip/data/text/news/hani/
