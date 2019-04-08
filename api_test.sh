#!/usr/bin/env bash

. deploy/config.sh

newman  -e test/$PORT.$FUNDCODE.smart-select.howinvest.com.postman_environment.json -c test/SmartSelect.postman_collection.json
