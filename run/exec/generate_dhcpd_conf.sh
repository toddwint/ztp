#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec -w /opt/ztp/scripts/ztp "$HOSTNAME" ./generate-dhcpd-conf.py
