#!/usr/bin/env bash
source config.txt

docker container stop "$HOSTNAME"
docker network rm "$HOSTNAME"-br
sudo ip link del "$HOSTNAME"-net
