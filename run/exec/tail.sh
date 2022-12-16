#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(dirname "$(realpath "$0")")")"
source "$SCRIPTDIR"/config.txt
set -x

docker exec -it "$HOSTNAME" bash -c '/opt/"$APPNAME"/scripts/tail.sh'
