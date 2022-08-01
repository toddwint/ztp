#!/usr/bin/env bash

## Run the commands to make it all work
ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata

echo $HOSTNAME > /etc/hostname

# Disable rsyslog kernel logs and start rsyslogd
sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
rsyslogd

# Check if folder exists and copy template files if not
# Also change permissions
if [ ! -d "/opt/ztp/script/ztp/ftp" ]
then
    cp -r /opt/ztp/scripts/ztp_template/. /opt/ztp/scripts/ztp/
    echo "Copied ztp_template to /opt/ztp/scripts/ztp"
    chown -R "${HUID}":"${HGID}" /opt/ztp/scripts/ztp
fi

# Configure isc-dhcp-server interfaces on which to listen
sed -Ei 's/INTERFACESv4=""/INTERFACESv4="eth0"/' /etc/default/isc-dhcp-server

# Get IP and subnet information and write over template files
IP=$(ip a show eth0 | sed -En 's/^\s+inet\s([0-9.]+).*/\1/p')
export IP
NET=$(ip a show eth0 | sed -En 's/^\s+inet\s(([0-9]{,3}.){2}[0-9]{,3}).*/\1/p')
export NET
sed -Ei 's/^(starting_ip_addr = .*)192.168.10/\1'"$NET"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py 
sed -Ei 's/^(file_server = .*)192.168.10.1/\1'"$IP"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py
sed -Ei 's/192.168.10/'"$NET"'/g' /opt/ztp/scripts/ztp/dhcpd.conf.template 
sed -Ei 's/^(\s+option (routers|domain-name-servers)) [0-9.]+;/\1 '"$IP"';/' /opt/ztp/scripts/ztp/dhcpd.conf.template
sed -Ei 's/^([# ]+option (tftp-server-name)) "[0-9.]+";/\1 "'"$IP"'";/' dhcpd.conf.template

# CD to script directory and run the python script
cd /opt/ztp/scripts/ztp
python3 generate-dhcpd-conf.py

# Keep docker running
bash
