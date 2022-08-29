#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec "$HOSTNAME" /opt/ztp/scripts/ztp/stop_tailon.sh
