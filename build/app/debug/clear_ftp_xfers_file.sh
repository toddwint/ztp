#!/usr/bin/env bash
set -x
truncate -s 0 /opt/"$APPNAME"/logs/vsftpd_xfers.log
