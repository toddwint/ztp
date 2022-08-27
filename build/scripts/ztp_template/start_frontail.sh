#!/usr/bin/env bash

IP=$(ip addr show eth0 | mawk '/ inet / {print $2}' | mawk -F/ '{print $1}')

echo -e 'Open your browser to `http://'"$IP"':'"$HTTPPORT"'` to see the logs\n'

frontail -d -p $HTTPPORT /var/log/syslog 2>&1 &
