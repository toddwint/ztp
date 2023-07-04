#!/usr/bin/env bash

FILE=/opt/"$APPNAME"/ftp/vendor_class_defaults.csv

if [ ! -f "$FILE" ]
    then
    echo "$FILE does not exist."
    exit 1
fi

set -x
column.py "$FILE"
