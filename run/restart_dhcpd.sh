#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" bash -c "service isc-dhcp-server stop; service isc-dhcp-server start"
