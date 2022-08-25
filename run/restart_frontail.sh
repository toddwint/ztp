#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/stop_frontail.sh"
docker exec "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/start_frontail.sh"
