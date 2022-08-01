#!/usr/bin/env bash
source config.txt
docker container stop "$HOSTNAME"
docker container rm "$HOSTNAME"
docker network rm "$HOSTNAME"-br
sudo ip link delete "$HOSTNAME"-net
