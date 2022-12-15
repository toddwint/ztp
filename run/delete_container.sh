#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"
source "${SCRIPTDIR}"/config.txt

# Stop and remove the container
docker container stop "$HOSTNAME"
docker container rm "$HOSTNAME"

# Remove the docker network and mgmt network
docker network rm "$HOSTNAME"
sudo ip link delete "$HOSTNAME"

# Remove the webadmin.html customized file
rm -rf "$SCRIPTDIR"/webadmin.html
