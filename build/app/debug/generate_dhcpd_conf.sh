#!/usr/bin/env bash
set -x

# Stop the transfer report daemon
kill $(cat /opt/"$APPNAME"/logs/generate_transfer_report.pid)

# Rerun dhcp generation scripts
/opt/"$APPNAME"/scripts/generate-dhcpd-conf.py

# Restart the transfer report daemon
nohup /opt/"$APPNAME"/scripts/generate_transfer_report.py >> /opt/"$APPNAME"/logs/generate_transfer_report.log 2>&1 &
echo $! > /opt/"$APPNAME"/logs/generate_transfer_report.pid

# Restart dhcp daemon
service isc-dhcp-server restart
