#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt
docker exec "$HOSTNAME" service rsyslog status
docker exec "$HOSTNAME" service isc-dhcp-server status
docker exec "$HOSTNAME" service vsftpd status
docker exec "$HOSTNAME" service tftpd-hpa status
docker exec "$HOSTNAME" bash -c 'if [ ! -z "$(pidof ttyd)" ]; then echo "ttyd is running"; else echo "ttyd is not running"; fi;'
docker exec "$HOSTNAME" bash -c 'if [ ! -z "$(pidof frontail)" ]; then echo "frontail is running"; else echo "frontail is not running"; fi;'
docker exec "$HOSTNAME" bash -c 'if [ ! -z "$(pidof tailon)" ]; then echo "tailon is running"; else echo "tailon is not running"; fi;'
