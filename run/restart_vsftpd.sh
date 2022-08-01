#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" bash -c "service vsftpd stop; service vsftpd start"
