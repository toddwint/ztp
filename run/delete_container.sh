#!/usr/bin/env bash
source "$(dirname "$(realpath $0)")"/config.txt
docker container stop "$HOSTNAME"
docker container rm "$HOSTNAME"
docker network rm "$HOSTNAME"
sudo ip link delete "$HOSTNAME"
htmlfile="$(dirname "$(realpath $0)")"/webadmin.html
rm -rf "$htmlfile"
