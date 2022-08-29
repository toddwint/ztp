#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# Tailon doesn't like --tty mode
docker exec "$HOSTNAME" /opt/ztp/scripts/ztp/start_tailon.sh
