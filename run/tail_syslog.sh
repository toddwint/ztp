#!/usr/bin/env bash
source config.txt

docker exec "$HOSTNAME" tail -f /var/log/syslog | grep -E 'dhcp|ftp'
