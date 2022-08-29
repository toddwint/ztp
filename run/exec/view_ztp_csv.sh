#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec "$HOSTNAME" cat /opt/ztp/scripts/ftp/ztp.csv
