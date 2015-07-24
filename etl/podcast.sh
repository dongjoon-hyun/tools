#!/bin/bash

# ESLPod
DIR=/hdfs/data/audio/speech/podcast/esl
for i in {164..1123}
do
	if [ ! -f $DIR/ESLPod$i.mp3 ];
	then
		curl -LO http://libsyn.com/media/eslpod/ESLPod$i.mp3
		mv ESLPod$i.mp3 $DIR
	fi
done
