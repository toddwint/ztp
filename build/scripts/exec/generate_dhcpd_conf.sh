#!/usr/bin/env bash
/opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
service isc-dhcp-server restart
