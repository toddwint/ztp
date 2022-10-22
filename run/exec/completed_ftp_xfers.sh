#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt
set -x
docker exec "$HOSTNAME" bash -c 'cat /opt/"$APPNAME"/logs/vsftpd_xfers.log 2> /dev/null'
