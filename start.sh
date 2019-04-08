#!/usr/bin/env bash

. deploy/config.sh

docker stop $(docker ps -q --filter ancestor=hopp-smart-api )

docker build -t hopp-smart-api -f Dockerfile .

docker run -v /app/logs:/app/logs/ -e API_PREFIX=fundrich -e SEARCH_FUND=True -e API_CANDIDATED=True -p $PORT:5000 -e TZ=Asia/Taipei -d hopp-smart-api