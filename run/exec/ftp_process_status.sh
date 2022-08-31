#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec "$HOSTNAME" ps ax -eo pid,lstart,cmd | grep vsftpd:
