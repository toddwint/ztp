#!/usr/bin/env bash
source "$(dirname "$(realpath $0)")"/config.txt
docker restart "$HOSTNAME"
