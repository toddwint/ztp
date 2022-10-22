#!/usr/bin/env bash
echo '
  Welcome to the '"$APPNAME"' docker image.
'
sleep 1s
tail -n 500 -F /opt/"$APPNAME"/logs/"$APPNAME".log
