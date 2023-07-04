#!/usr/bin/env bash

/opt/"$APPNAME"/scripts/generate_transfer_report.py

FILE=/opt/"$APPNAME"/ftp/transfer_report.csv

if [ ! -f "$FILE" ]
    then
    echo "$FILE does not exist."
    exit 1
fi

set -x
column.py "$FILE" | fzf --reverse --header-lines=1
