#!/usr/bin/env bash

## Run the commands to make it all work
ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata

echo $HOSTNAME > /etc/hostname

# Disable rsyslog kernel logs and start rsyslogd
sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
rsyslogd

# Check if folder exists and copy template files if not
# Also change permissions and create ftp folders
if [ ! -d "/opt/ztp/script/ztp/ftp" ]
then
    cp -r /opt/ztp/scripts/ztp_template/. /opt/ztp/scripts/ztp/
    echo "Copied ztp_template to /opt/ztp/scripts/ztp"
    mkdir -p /opt/ztp/scripts/ztp/ftp/os_images
    mkdir -p /opt/ztp/scripts/ztp/ftp/config_files
    chown -R "${HUID}":"${HGID}" /opt/ztp/scripts/ztp
fi

# Configure isc-dhcp-server interfaces on which to listen
sed -Ei 's/INTERFACESv4=""/INTERFACESv4="eth0"/' /etc/default/isc-dhcp-server

# Get IP and subnet information and save to env variables
IPCALC=$(ipcalc -nb $(ip addr show eth0 | awk '/\<inet\>/ {print $2}'))
IP=$(echo "$IPCALC" | awk '/Address/ {print $2}')
NETMASK=$(echo "$IPCALC" | awk '/Netmask/ {print $2}')
NETMASKBITS=$(echo "$IPCALC" | awk '/Netmask/ {print $4}')
NETWORK=$(echo "$IPCALC" | awk '/Network/ {print $2}')
NETWORKADDR=$(echo "$IPCALC" | awk -F' *|/' '/Network/ {print $2}')
HOSTMIN=$(echo "$IPCALC" | awk '/HostMin/ {print $2}')
HOSTMAX=$(echo "$IPCALC" | awk '/HostMax/ {print $2}')
BROADCAST=$(echo "$IPCALC" | awk '/Broadcast/ {print $2}')
DHCPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 5)")
DHCPEND=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 1)")
IPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$IP') + 1)")
export IPCALC
export IP
export NETMASK
export NETMASKBITS
export NETWORK
export NETWORKADDR
export HOSTMIN
export HOSTMAX
export BROADCAST
export DHCPSTART
export DHCPEND

# Python generate-dhcpd-conf.py modifications
sed -Ei 's/^(#?starting_ip_addr =).*192.168.*/\1 '"'$IPSTART'"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py 
sed -Ei 's/^(file_server =).*192.168.*/\1 '"'$IP'"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py
sed -Ei 's/^(gateway =).*192.168.*/\1 '"'$GATEWAY'"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py
sed -Ei 's/8080/'"$HTTPPORT"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py
sed -Ei 's/8081/'"$(expr $HTTPPORT + 1)"'/' /opt/ztp/scripts/ztp/generate-dhcpd-conf.py

# isc-dhcp-server template modifications
sed -Ei 's/^(subnet) 192.168.10.0 (netmask).*/\1 '"$NETWORKADDR"' \2 '"$NETMASK"' {/' /opt/ztp/scripts/ztp/dhcpd.conf.template 
sed -Ei 's/^(\s+range).*/\1 '"$DHCPSTART"' '"$DHCPEND"';/' /opt/ztp/scripts/ztp/dhcpd.conf.template 
sed -Ei 's/^(\s+option subnet-mask).*/\1 '"$NETMASK"';/' /opt/ztp/scripts/ztp/dhcpd.conf.template 
sed -Ei 's/^(\s+option broadcast-address).*/\1 '"$BROADCAST"';/' /opt/ztp/scripts/ztp/dhcpd.conf.template 
sed -Ei 's/^(\s+option (routers|domain-name-servers)) [0-9.]+;/\1 '"$IP"';/' /opt/ztp/scripts/ztp/dhcpd.conf.template
sed -Ei 's/^([# ]+option (tftp-server-name)) "[0-9.]+";/\1 "'"$IP"'";/' /opt/ztp/scripts/ztp/dhcpd.conf.template

# CD to script directory and run the python script
cd /opt/ztp/scripts/ztp
python3 generate-dhcpd-conf.py

# Keep docker running
bash
