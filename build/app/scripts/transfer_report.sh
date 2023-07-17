#!/usr/bin/env bash
echo '
  Welcome to the '"$APPNAME"' docker image.
'
sleep 1s
/opt/"$APPNAME"/scripts/transfer_report.py
