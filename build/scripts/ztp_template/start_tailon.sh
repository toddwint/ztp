#!/usr/bin/env bash

IP=$(ip addr show eth0 | mawk '/ inet / {print $2}' | mawk -F/ '{print $1}')

echo -e 'Open your browser to `http://'"$IP"':'"$(expr $HTTPPORT + 1)"'` to see the logs\n'

nohup tailon -b 0.0.0.0:$(expr $HTTPPORT + 1) /var/log/syslog /etc/dhcp/dhcpd.conf /etc/vsftpd.conf /etc/default/tftpd-hpa /var/lib/dhcp/dhcpd.leases /opt/ztp/scripts/ftp/ztp.csv >> /opt/ztp/scripts/tailon.nohup 2>&1 &
