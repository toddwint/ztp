#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"
source "$SCRIPTDIR"/config.txt
set -x

docker exec -it "$HOSTNAME" bash
