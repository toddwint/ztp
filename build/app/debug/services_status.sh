#!/usr/bin/env bash
bash -c 'if [ ! -z "$(pidof rsyslogd)" ]; then echo "rsyslogd is running"; else echo "rsyslogd is not running"; fi;'
service isc-dhcp-server status
service vsftpd status
service tftpd-hpa status
bash -c 'if [ ! -z "$(pidof ttyd)" ]; then echo "ttyd is running"; else echo "ttyd is not running"; fi;'
bash -c 'if [ ! -z "$(pidof frontail)" ]; then echo "frontail is running"; else echo "frontail is not running"; fi;'
bash -c 'if [ ! -z "$(pidof tailon)" ]; then echo "tailon is running"; else echo "tailon is not running"; fi;'
