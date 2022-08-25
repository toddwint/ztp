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
if [ ! -d "/opt/ztp/scripts/ztp/ftp" ]
then
    mkdir -p /opt/ztp/scripts/ztp/ftp/os_images
    mkdir -p /opt/ztp/scripts/ztp/ftp/config_files
    cp -r /opt/ztp/scripts/ztp_template/. /opt/ztp/scripts/ztp/
    echo "Copied ztp_template to /opt/ztp/scripts/ztp"
    chown -R "${HUID}":"${HGID}" /opt/ztp/scripts/ztp
fi

# Configure isc-dhcp-server interfaces on which to listen
sed -Ei 's/INTERFACESv4=""/INTERFACESv4="eth0"/' /etc/default/isc-dhcp-server


# Get IP and subnet information and save to env variables

# Using `ipcalc` (apt install ipcalc) (adds ~50 MB to docker image)
#IPCALC=$(ipcalc -nb "$SUBNET")
#export IPCALC
#IP=$(ip addr show eth0 | mawk '/ inet / {print $2}' | mawk -F/ '{print $1}')
#NETMASK=$(echo "$IPCALC" | mawk '/Netmask/ {print $2}')
#NETMASKBITS=$(echo "$IPCALC" | mawk '/Netmask/ {print $4}')
#NETWORK=$(echo "$IPCALC" | mawk '/Network/ {print $2}')
#NETWORKADDR=$(echo "$IPCALC" | mawk '/Network/ {print $2}' | mawk -F/ '{print $1}')
#HOSTMIN=$(echo "$IPCALC" | mawk '/HostMin/ {print $2}')
#HOSTMAX=$(echo "$IPCALC" | mawk '/HostMax/ {print $2}')
#BROADCAST=$(echo "$IPCALC" | mawk '/Broadcast/ {print $2}')
#DHCPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 5)")
#DHCPEND=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 1)")
#IPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$IP') + 1)")

# Using python module `netaddr` (pip3 install netaddr) (adds ~10 MB to docker image)
IP=$(ip addr show eth0 | mawk '/ inet / {print $2}' | mawk -F/ '{print $1}')
NETMASK=$(python3 -c "import netaddr; print(netaddr.IPNetwork('$SUBNET').netmask)")
NETMASKBITS=$(python3 -c "import netaddr; print(netaddr.IPNetwork('$SUBNET').prefixlen)")
NETWORK=$(python3 -c "import netaddr; print(netaddr.IPNetwork('$SUBNET').cidr)")
NETWORKADDR=$(python3 -c "import netaddr; print(netaddr.IPNetwork('$SUBNET').network)")
HOSTMIN=$(python3 -c "import netaddr; print(netaddr.IPAddress(netaddr.IPNetwork('$SUBNET').first + 1))")
HOSTMAX=$(python3 -c "import netaddr; print(netaddr.IPAddress(netaddr.IPNetwork('$SUBNET').last - 1))")
BROADCAST=$(python3 -c "import netaddr; print(netaddr.IPNetwork('$SUBNET').broadcast)")
DHCPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 5)")
DHCPEND=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 1)")
IPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$IP') + 1)")

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
export IPSTART


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
