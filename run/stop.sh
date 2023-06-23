#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"
source "${SCRIPTDIR}"/config.txt

# Backup log files
docker exec -it "$HOSTNAME" bash -c '/opt/"$APPNAME"/debug/save_transfer_report.sh'

docker stop "$HOSTNAME"
