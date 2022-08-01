#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" bash -c "cd /opt/ztp/scripts/ztp && python3 generate-dhcpd-conf.py"
