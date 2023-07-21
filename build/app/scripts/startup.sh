#!/usr/bin/env bash

## Run the commands to make it all work
ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata

echo $HOSTNAME > /etc/hostname

# Extract compressed binaries and move binaries to bin
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    # Unzip frontail and tailon
    gunzip /usr/local/bin/frontail.gz
    gunzip /usr/local/bin/tailon.gz

    # Copy python scripts to /usr/local/bin and make executable
    cp /opt/"$APPNAME"/scripts/ipcalc.py /usr/local/bin
    cp /opt/"$APPNAME"/scripts/increment_mac.py /usr/local/bin
    cp /opt/"$APPNAME"/scripts/mactools.py /usr/local/bin
    cp /opt/"$APPNAME"/scripts/column.py /usr/local/bin
    chmod 775 /usr/local/bin/ipcalc.py
    chmod 775 /usr/local/bin/increment_mac.py
    chmod 775 /usr/local/bin/mactools.py
    chmod 775 /usr/local/bin/column.py
fi

# Link scripts to debug folder as needed
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    ln -s /opt/"$APPNAME"/scripts/tail.sh /opt/"$APPNAME"/debug
    ln -s /opt/"$APPNAME"/scripts/tmux.sh /opt/"$APPNAME"/debug
    ln -s /opt/"$APPNAME"/scripts/transfer_report.sh /opt/"$APPNAME"/debug
fi

# Create the file /var/run/utmp or when using tmux this error will be received
# utempter: pututline: No such file or directory
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    touch /var/run/utmp
else
    truncate -s 0 /var/run/utmp
fi

# Disable rsyslog kernel logs and start rsyslogd
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    sed -Ei '/imklog/s/^([^#])/#\1/' /etc/rsyslog.conf
    sed -Ei '/immark/s/^#//' /etc/rsyslog.conf
    rm -rf /var/log/syslog
else
    truncate -s 0 /var/log/syslog
fi

# Sometimes rsyslog does not start, so start it and then try again
#service rsyslog start # ubuntu:focal
rsyslogd #ubuntu:jammy
if [ -z $(pidof rsyslogd) ]; then
    echo 'rsyslog not running'
    #service rsyslog start # ubuntu:focal
    rsyslogd #ubuntu:jammy
else
    echo 'rsyslog is running'
fi

# Link the log to the app log. Create/clear other log files.
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    mkdir -p /opt/"$APPNAME"/logs
    ln -s /var/log/syslog /opt/"$APPNAME"/logs/"$APPNAME".log
    touch /opt/"$APPNAME"/logs/vsftpd_xfers.log
    #touch /opt/"$APPNAME"/logs/webfsd.log
    #chown www-data:www-data /opt/"$APPNAME"/logs/webfsd.log
else
    truncate -s 0 /opt/"$APPNAME"/logs/vsftpd_xfers.log
    #truncate -s 0 /opt/"$APPNAME"/logs/webfsd.log
fi

# Print first message to either the app log file or syslog
#echo "$(date -Is) [Start of $APPNAME log file]" >> /opt/"$APPNAME"/logs/"$APPNAME".log
logger "[Start of $APPNAME log file]"

# Check if `ftp` subfolder exists. If non-existing, create it.
# Checking for a file inside the folder because if the folder
#  is mounted as a volume it will already exists when docker starts.
# Also change permissions
if [ ! -e "/opt/$APPNAME/ftp/.exists" ]
then
    mkdir -p /opt/"$APPNAME"/ftp/os_images
    mkdir -p /opt/"$APPNAME"/ftp/config_files
    touch /opt/"$APPNAME"/ftp/.exists
    echo '`ftp` folder created'
    cp /opt/"$APPNAME"/configs/ztp.csv.template /opt/"$APPNAME"/ftp/ztp.csv
    cp /opt/"$APPNAME"/configs/vendor_class_defaults.csv /opt/"$APPNAME"/ftp/
    cp /opt/"$APPNAME"/configs/supported_device_models.json /opt/"$APPNAME"/ftp/
    cp /opt/"$APPNAME"/scripts/csv_filter.py /opt/"$APPNAME"/ftp/
    echo "Copied files to /opt/$APPNAME/ftp"
    chown -R "${HUID}":"${HGID}" /opt/"$APPNAME"/ftp
fi

# Calculate network values
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    # Get IP and subnet information and save to env variables
    # Using python script `ipcalc.py` (adds ~1.6 KB to docker image)
    ipcalc.py $(ip addr show eth0 | mawk '/ inet / {print $2}') > /opt/"$APPNAME"/configs/ipcalc.txt
    IP=$(ip addr show eth0 | mawk '/ inet / {print $2}' | mawk -F/ '{print $1}')
    SUBNET=$(mawk '/Network:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    NETMASK=$(mawk '/Netmask:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    NETMASKBITS=$(mawk '/Netmask_Bits:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    NETWORK=$(mawk '/Network:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    NETWORKADDR=$(mawk '/Network_Addr:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    HOSTMIN=$(mawk '/Host_Min:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    HOSTMAX=$(mawk '/Host_Max:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    BROADCAST=$(mawk '/Broadcast:/ {print $2}' /opt/"$APPNAME"/configs/ipcalc.txt)
    DHCPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 5)")
    DHCPEND=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 4)")
    IPSTART=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMIN') + 0)")
    if [ -z "$MGMTIP" ]; then
        MGMTIP=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 2)")
    fi
    if [ -z "$GATEWAY" ]; then
        GATEWAY=$(python3 -c "import ipaddress; print(ipaddress.ip_address('$HOSTMAX') - 0)")
    fi
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
    export MGMTIP
    export GATEWAY
fi

# Modify configuration files or customize container
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    # Make copies of template files
    cp /opt/"$APPNAME"/configs/dhcpd.conf.template /opt/"$APPNAME"/configs/dhcpd.conf
    cp /opt/"$APPNAME"/configs/vsftpd.conf.template /opt/"$APPNAME"/configs/vsftpd.conf
    cp /opt/"$APPNAME"/configs/tftpd-hpa.template /opt/"$APPNAME"/configs/tftpd-hpa
    cp /opt/"$APPNAME"/configs/webfsd.conf.template /opt/"$APPNAME"/configs/webfsd.conf

    # python generate-dhcpd-conf.py modifications
    sed -Ei 's/^(starting_ip =).*192.168.*/\1 '"'$IPSTART'"'/' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
    sed -Ei 's/^(file_server =).*192.168.*/\1 '"'$IP'"'/' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
    sed -Ei 's/^(mgmt_ip =).*192.168.*/\1 '"'$MGMTIP'"'/' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
    sed -Ei 's/^(gateway =).*192.168.*/\1 '"'$GATEWAY'"'/' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
    sed -Ei 's/^(dhcp_start =).*192.168.*/\1 '"'$DHCPSTART'"'/' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
    sed -Ei 's/^(dhcp_end =).*192.168.*/\1 '"'$DHCPEND'"'/' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py
    sed -i 's#/opt/ztp/#/opt/'"$APPNAME"'/#' /opt/"$APPNAME"/scripts/generate-dhcpd-conf.py

    # Configure isc-dhcp-server interfaces on which to listen
    sed -Ei 's/INTERFACESv4=""/INTERFACESv4="eth0"/' /etc/default/isc-dhcp-server
    sed -Ei 's/INTERFACESv6=""/#INTERFACESv6=""/' /etc/default/isc-dhcp-server

    # isc-dhcp-server template modifications
    sed -Ei 's/^(subnet) 192.168.10.0 (netmask).*/\1 '"$NETWORKADDR"' \2 '"$NETMASK"' {/' /opt/"$APPNAME"/configs/dhcpd.conf
    sed -Ei 's/^(\s+range).*/\1 '"$DHCPSTART"' '"$DHCPEND"';/' /opt/"$APPNAME"/configs/dhcpd.conf
    sed -Ei 's/^(\s+option subnet-mask).*/\1 '"$NETMASK"';/' /opt/"$APPNAME"/configs/dhcpd.conf
    sed -Ei 's/^(\s+option broadcast-address).*/\1 '"$BROADCAST"';/' /opt/"$APPNAME"/configs/dhcpd.conf
    sed -Ei 's/^(\s+option (routers|domain-name-servers)) [0-9.]+;/\1 '"$IP"';/' /opt/"$APPNAME"/configs/dhcpd.conf
    sed -Ei 's/^([# ]+option (tftp-server-name)) "[0-9.]+";/\1 "'"$IP"'";/' /opt/"$APPNAME"/configs/dhcpd.conf

    # vsftpd template modifications
    sed -Ei 's#^((anon|local)_root=).*#\1/opt/'"$APPNAME"'/ftp#' /opt/"$APPNAME"/configs/vsftpd.conf
    sed -Ei 's#^(xferlog_file=).*#\1/opt/'"$APPNAME"'/logs/vsftpd_xfers.log#' /opt/"$APPNAME"/configs/vsftpd.conf

    # tftpd-hpa template modifications
    sed -Ei 's#^(TFTP_DIRECTORY).*#\1="/opt/'"$APPNAME"'/ftp"#' /opt/"$APPNAME"/configs/tftpd-hpa

    # webfsd template modifications
    sed -Ei '/^web_root=/c web_root="/opt/'"$APPNAME"'/ftp"' /opt/"$APPNAME"/configs/webfsd.conf
    #sed -Ei '/^web_accesslog=/c web_accesslog="/opt/'"$APPNAME"'/logs/webfsd.log"' /opt/"$APPNAME"/configs/webfsd.conf

    # Copy templates to configuration locations
    cp /opt/"$APPNAME"/configs/dhcpd.conf /etc/dhcp/dhcpd.conf
    cp /opt/"$APPNAME"/configs/vsftpd.conf /etc/vsftpd.conf
    cp /opt/"$APPNAME"/configs/tftpd-hpa /etc/default/tftpd-hpa
    cp /opt/"$APPNAME"/configs/webfsd.conf /etc/webfsd.conf
fi

# Run the python script
/opt/"$APPNAME"/scripts/generate-dhcpd-conf.py

# Run the python daemon to update transfer report
nohup /opt/"$APPNAME"/scripts/generate_transfer_report.py >> /opt/"$APPNAME"/logs/generate_transfer_report.log 2>&1 &
echo $! > /opt/"$APPNAME"/logs/generate_transfer_report.pid

# Remove service pid(s) if it exists.
rm -rf /var/run/dhcpd.pid
rm -rf /var/run/webfs/webfsd.pid

# Start services
service vsftpd start
service tftpd-hpa start
service webfs start
service isc-dhcp-server start


# Start web interface
NLINES=1000 # how many tail lines to follow

# ttyd1 (tail and read only)
# to remove color add the option `-T xterm-mono`
# selection changed to selectionBackground in 1.7.2 - bug reported
# `-t 'theme={"foreground":"black","background":"white", "selection":"#ff6969"}'` # 69, nice!
# `-t 'theme={"foreground":"black","background":"white", "selectionBackground":"#ff6969"}'`
sed -Ei 's/tail -n 500/tail -n '"$NLINES"'/' /opt/"$APPNAME"/scripts/tail.sh
#nohup ttyd -p "$HTTPPORT1" -R -t titleFixed="${APPNAME}.log" -t fontSize=16 -t 'theme={"foreground":"black","background":"white", "selectionBackground":"#ff6969"}' -s 2 /opt/"$APPNAME"/scripts/tail.sh >> /opt/"$APPNAME"/logs/ttyd1.log 2>&1 &
nohup ttyd -p "$HTTPPORT1" -R -t titleFixed="${APPNAME}.log" -t fontSize=16 -t 'theme={"foreground":"black","background":"white", "selectionBackground":"#ff6969"}' -s 2 /opt/"$APPNAME"/scripts/transfer_report.sh >> /opt/"$APPNAME"/logs/ttyd1.log 2>&1 &

# ttyd2 (tmux with color)
# to remove color add the option `-T xterm-mono`
# selection changed to selectionBackground in 1.7.2 - bug reported
# `-t 'theme={"foreground":"black","background":"white", "selection":"#ff6969"}'` # 69, nice!
# `-t 'theme={"foreground":"black","background":"white", "selectionBackground":"#ff6969"}'`
cp /opt/"$APPNAME"/configs/tmux.conf /root/.tmux.conf
sed -Ei 's/tail -n 500/tail -n '"$NLINES"'/' /opt/"$APPNAME"/scripts/tmux.sh
nohup ttyd -p "$HTTPPORT2" -t titleFixed="${APPNAME}.log" -t fontSize=16 -t 'theme={"foreground":"black","background":"white", "selectionBackground":"#ff6969"}' -s 9 /opt/"$APPNAME"/scripts/tmux.sh >> /opt/"$APPNAME"/logs/ttyd2.log 2>&1 &

# frontail
nohup frontail -n "$NLINES" -p "$HTTPPORT3" /opt/"$APPNAME"/logs/"$APPNAME".log >> /opt/"$APPNAME"/logs/frontail.log 2>&1 &

# tailon
sed -Ei 's/\$lines/'"$NLINES"'/' /opt/"$APPNAME"/configs/tailon.toml
sed -Ei '/^listen-addr = /c listen-addr = [":'"$HTTPPORT4"'"]' /opt/"$APPNAME"/configs/tailon.toml
nohup tailon -c /opt/"$APPNAME"/configs/tailon.toml /opt/"$APPNAME"/logs/"$APPNAME".log /opt/"$APPNAME"/logs/vsftpd_xfers.log /etc/dhcp/dhcpd.conf /etc/vsftpd.conf /etc/default/tftpd-hpa /var/lib/dhcp/dhcpd.leases /opt/"$APPNAME"/ftp/ztp.csv /opt/"$APPNAME"/logs/ttyd1.log /opt/"$APPNAME"/logs/ttyd2.log /opt/"$APPNAME"/logs/frontail.log /opt/"$APPNAME"/logs/tailon.log >> /opt/"$APPNAME"/logs/tailon.log 2>&1 &

# Remove the .firstrun file if this is the first run
if [ -e /opt/"$APPNAME"/scripts/.firstrun ]; then
    rm -f /opt/"$APPNAME"/scripts/.firstrun
fi

# Keep docker running
bash
