#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"
source "${SCRIPTDIR}"/config.txt

docker restart "$HOSTNAME"
