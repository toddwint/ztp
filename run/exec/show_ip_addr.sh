#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec "$HOSTNAME" ip addr show eth0
