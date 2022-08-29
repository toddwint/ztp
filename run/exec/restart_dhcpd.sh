#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec "$HOSTNAME" bash -c 'service isc-dhcp-server stop; if [ ! -z "$(pidof dhcpd)" ]; then kill $(pidof dhcpd); fi; service isc-dhcp-server start'
