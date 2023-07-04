---
title: README
---

# toddwint/ztp

## Info

`ZTP` (Zero-Touch Provisioning) docker image for Juniper SRX345, SRX1500, ACX7024, EX2300, EX4100, and HPE Aruba 2930F devices.

Docker Hub: <https://hub.docker.com/r/toddwint/ztp>

GitHub: <https://github.com/toddwint/ztp>

_For more detailed information, please view the `ZTP Instructions` file [here](ZTP Instructions.md), [here](ZTP Instructions.html), or [here](ZTP Instructions.pdf)._


## Overview

- Performs Zero-Touch Provisioning of
    - Juniper SRX345
    - Juniper SRX1500
    - Juniper ACX7024
    - Juniper EX2300
    - Juniper EX4100
    - HPE Aruba 2930F


## Features

- Ubuntu base image
- Plus:
  - rsyslog
  - isc-dhcp-server
  - ftp
  - vsftpd
  - tftp-hpa
  - tftpd-hpa
  - webfs
  - bsdmainitils
  - fzf
  - tmux
  - python3-minimal
  - iproute2
  - tzdata
  - [ttyd](https://github.com/tsl0922/ttyd)
    - View the terminal in your browser
  - [frontail](https://github.com/mthenw/frontail)
    - View logs in your browser
    - Mark/Highlight logs
    - Pause logs
    - Filter logs
  - [tailon](https://github.com/gvalkov/tailon)
    - View multiple logs and files in your browser
    - User selectable `tail`, `grep`, `sed`, and `awk` commands
    - Filter logs and files
    - Download logs to your computer


## Sample `config.txt` file

```
# To get a list of timezones view the files in `/usr/share/zoneinfo`
TZ=UTC

# The interface on which to set the IP. Run `ip -br a` to see a list
INTERFACE=eth0

# The IP address that will be set on the docker container
# The last 4 IPs in the subnet are available for use.
IPADDR=172.21.255.252

# The IP address that will be set on the host to manage the docker container
# The last 4 IPs in the subnet are available for use.
MGMTIP=172.21.255.253

# The IP subnet in the form NETWORK/PREFIX
SUBNET=172.21.0.0/16

# The IP of the gateway. 
# Don't leave blank. Enter a valid ip from the subnet range
# The last 4 IPs in the subnet are available for use.
GATEWAY=172.21.255.254

# The ports for web management access of the docker container.
# ttyd tail, ttyd tmux, frontail, and tmux respectively
HTTPPORT1=8080
HTTPPORT2=8081
HTTPPORT3=8082
HTTPPORT4=8083

# The hostname of the instance of the docker container
HOSTNAME=ztp01
```


## Sample docker run script

```
#!/usr/bin/env bash
REPO=toddwint
APPNAME=ztp
HUID=$(id -u)
HGID=$(id -g)
SCRIPTDIR="$(dirname "$(realpath "$0")")"
source "$SCRIPTDIR"/config.txt

# Make the macvlan needed to listen on ports
# Set the IP on the host and add a route to the container
docker network create -d macvlan --subnet="$SUBNET" --gateway="$GATEWAY" \
  --aux-address="mgmt_ip=$MGMTIP" -o parent="$INTERFACE" \
  "$HOSTNAME"
sudo ip link add "$HOSTNAME" link "$INTERFACE" type macvlan mode bridge
sudo ip addr add "$MGMTIP"/32 dev "$HOSTNAME"
sudo ip link set "$HOSTNAME" up
sudo ip route add "$IPADDR"/32 dev "$HOSTNAME"

# Create the docker container
docker run -dit \
    --name "$HOSTNAME" \
    --network "$HOSTNAME" \
    --ip $IPADDR \
    -h "$HOSTNAME" \
    ` # Volume can be changed to another folder. For Example: ` \
    ` # -v /home/"$USER"/Desktop/ftp:/opt/"$APPNAME"/ftp \ ` \
    -v "$SCRIPTDIR"/ftp:/opt/"$APPNAME"/ftp \
    -e TZ="$TZ" \
    -e MGMTIP="$MGMTIP" \
    -e GATEWAY="$GATEWAY" \
    -e HUID="$HUID" \
    -e HGID="$HGID" \
    -e HTTPPORT1="$HTTPPORT1" \
    -e HTTPPORT2="$HTTPPORT2" \
    -e HTTPPORT3="$HTTPPORT3" \
    -e HTTPPORT4="$HTTPPORT4" \
    -e HOSTNAME="$HOSTNAME" \
    -e APPNAME="$APPNAME" \
    `# --cap-add=NET_ADMIN \ ` \
    ${REPO}/${APPNAME}
```


## Login page

Open the `webadmin.html` file.

- Or just type in your browser: 
  - `http://<ip_address>:<port1>` or
  - `http://<ip_address>:<port2>` or
  - `http://<ip_address>:<port3>`
  - `http://<ip_address>:<port4>`
