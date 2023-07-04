#!/usr/bin/env bash

USRFILE=/opt/"$APPNAME"/ftp/supported_device_models.json
DEFFILE=/opt/"$APPNAME"/configs/supported_device_models.json

if [ ! -f "$USRFILE" ]
    then
    echo "$USRFILE does not exist. $DEFFILE will be used instead."
    FILE=$DEFFILE
else
    FILE=$USRFILE
fi

set -x
cat "$FILE"
