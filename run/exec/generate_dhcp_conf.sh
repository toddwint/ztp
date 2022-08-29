#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec -w /opt/ztp/scripts/ztp "$HOSTNAME" /opt/ztp/scripts/ztp/generate-dhcpd-conf.py
