#!/usr/bin/env bash

echo -e 'Open your browser to `http://127.0.0.1:'"$(expr $HTTPPORT + 1)"'` to see the logs\n'

nohup tailon -b:$(expr $HTTPPORT + 1) /var/log/syslog /etc/dhcp/dhcpd.conf /etc/vsftpd.conf /etc/default/tftpd-hpa /var/lib/dhcp/dhcpd.leases /opt/ztp/scripts/ztp/ztp.csv >> /opt/ztp/scripts/tailon.nohup &
