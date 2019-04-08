#!/usr/bin/env bash

. deploy/config.sh

docker stop $(docker ps -q --filter ancestor=ocr )

docker build -t ocr -f Dockerfile .

docker run -v /app/logs:/app/logs/ -p $PORT:5000 -e TZ=Asia/Taipei -d ocr