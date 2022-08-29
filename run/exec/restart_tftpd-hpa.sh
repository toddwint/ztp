#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

docker exec "$HOSTNAME" bash -c "service tftpd-hpa stop; service tftpd-hpa start"
