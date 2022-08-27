#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# Note: leave the `-it` options in.
# -i, --interactive[=false]    Keep STDIN open even if not attached
# -t, --tty[=false]            Allocate a pseudo-TTY

docker exec -it "$HOSTNAME" bash -c "cd /opt/ztp/scripts/ztp && python3 generate-dhcpd-conf.py"

# Frontail in daemon mode doesn't like --tty mode
docker exec -i "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/stop_frontail.sh"
docker exec -i "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/start_frontail.sh"
