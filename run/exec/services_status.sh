#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# Note: leave the `-it` options in.
# -i, --interactive[=false]    Keep STDIN open even if not attached
# -t, --tty[=false]            Allocate a pseudo-TTY

docker exec -it "$HOSTNAME" bash -c "service isc-dhcp-server status"
docker exec -it "$HOSTNAME" bash -c "service vsftpd status"
docker exec -it "$HOSTNAME" bash -c "service tftpd-hpa status"
