#!/usr/bin/env bash
set -x

FILE=/opt/"$APPNAME"/logs/transfer_report.csv

if [ ! -f "$FILE" ]
    then
    echo "$FILE does not exist."
    exit 1
fi

column.py "$FILE"
