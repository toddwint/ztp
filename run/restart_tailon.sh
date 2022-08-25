#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/stop_tailon.sh"
docker exec "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/start_tailon.sh"
