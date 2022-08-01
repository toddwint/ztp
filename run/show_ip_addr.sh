#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" ip addr show eth0
