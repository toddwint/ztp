#!/usr/bin/env bash

echo -e 'Open your browser to `http://127.0.0.1:'"$HTTPPORT"'` to see the logs\n'

frontail -d -p $HTTPPORT /var/log/syslog &
