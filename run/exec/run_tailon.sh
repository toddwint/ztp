#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# Note: leave the `-it` options in.
# -i, --interactive[=false]    Keep STDIN open even if not attached
# -t, --tty[=false]            Allocate a pseudo-TTY

docker exec -it "$HOSTNAME" bash -c "/opt/ztp/scripts/ztp/start_tailon.sh"

## Extra commands used while troubleshooting. Didn't want to lose these.
#docker exec -dit "$HOSTNAME" bash -c "tailon -b 0.0.0.0:$(expr $HTTPPORT + 1) /var/log/syslog /etc/dhcp/dhcpd.conf /etc/vsftpd.conf /etc/default/tftpd-hpa /var/lib/dhcp/dhcpd.leases /opt/ztp/scripts/ftp/ztp.csv"
#nohup tailon -b 0.0.0.0:$(expr $HTTPPORT + 1) /var/log/syslog /etc/dhcp/dhcpd.conf /etc/vsftpd.conf /etc/default/tftpd-hpa /var/lib/dhcp/dhcpd.leases /opt/ztp/scripts/ftp/ztp.csv >> /opt/ztp/scripts/tailon.nohup &
