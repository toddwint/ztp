#!/usr/bin/env bash
APPNAME=ztp
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt
set -x
docker exec -it "$HOSTNAME" tmux attach-session -t "$APPNAME"
