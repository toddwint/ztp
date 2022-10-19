#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec -w /opt/ztp/scripts "$HOSTNAME" ./generate-dhcpd-conf.py
docker exec "$HOSTNAME" service isc-dhcp-server restart
