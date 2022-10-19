#!/usr/bin/env bash
set -x
/opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
service isc-dhcp-server restart
