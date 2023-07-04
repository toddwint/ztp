#!/usr/bin/env bash
echo '
  Welcome to the '"$APPNAME"' docker image.
'
sleep 1s
while :
do
    /opt/"$APPNAME"/scripts/generate_transfer_report.py
    column.py /opt/"$APPNAME"/ftp/transfer_report.csv
    sleep 15
    clear
done
