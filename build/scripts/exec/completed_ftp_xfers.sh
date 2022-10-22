#!/usr/bin/env bash
set -x
cat /opt/"$APPNAME"/logs/vsftpd_xfers.log 2> /dev/null
