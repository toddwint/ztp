#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt
set -x
docker exec "$HOSTNAME" truncate -s 0 /var/log/syslog
