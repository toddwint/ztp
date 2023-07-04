#!/usr/bin/env bash

FILE=/opt/"$APPNAME"/ftp/ztp.csv

if [ ! -f "$FILE" ]
    then
    echo "$FILE does not exist."
    exit 1
fi

set -x
column.py "$FILE"
