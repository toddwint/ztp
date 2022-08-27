#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# Note: leave the `-it` options in.
# -i, --interactive[=false]    Keep STDIN open even if not attached
# -t, --tty[=false]            Allocate a pseudo-TTY

# Frontail in daemon mode doesn't like --tty mode
docker exec -i "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/stop_frontail.sh"
docker exec -i "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/start_frontail.sh"
