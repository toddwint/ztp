#!/usr/bin/env bash
APPNAME=ztp
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt
set -x
docker exec -w /opt/"$APPNAME"/scripts "$HOSTNAME" ./generate-dhcpd-conf.py
docker exec "$HOSTNAME" service isc-dhcp-server restart
