#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# Frontail in daemon mode doesn't like --tty mode
docker exec "$HOSTNAME" /opt/ztp/scripts/ztp/stop_frontail.sh
docker exec "$HOSTNAME" /opt/ztp/scripts/ztp/start_frontail.sh
