#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" bash -c "service tftpd-hpa stop; service tftpd-hpa start"
