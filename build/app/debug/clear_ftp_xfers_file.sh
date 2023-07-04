#!/usr/bin/env bash

FILE=/opt/"$APPNAME"/logs/vsftpd_xfers.log

if [ ! -f "$FILE" ]
    then
    echo "$FILE does not exist."
    exit 1
fi

set -x
truncate -s 0 "$FILE"
