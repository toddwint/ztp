---
title: README
author: Todd Wintermute
date: 2025-11-09
---

# toddwint/ztp


## Info

`ZTP` (Zero-Touch Provisioning) docker image for Juniper SRX345, SRX1500, ACX7024, EX2300, EX4100, and HPE Aruba 2930F devices.

Docker Hub: <https://hub.docker.com/r/toddwint/ztp>

GitHub: <https://github.com/toddwint/ztp>

_For more detailed information, please view the `ZTP_Instructions` files: `ZTP_Instructions.md`, `ZTP_Instructions.html`, or `ZTP_Instructions.pdf`._


## Overview

Docker image for performing Zero-Touch Provisioning of network devices.

- Supports the following devices:
    - Juniper SRX345
    - Juniper SRX1500
    - Juniper ACX7024
    - Juniper EX2300
    - Juniper EX4100
    - HPE Aruba 2930F

Pull the docker image from Docker Hub or, optionally, build the docker image from the source files in the `build` directory.

Create and run the container using `docker run` commands, `docker compose` commands, or by downloading and using the files here on github in the directories `run` or `compose`.

**NOTE: A volume named `ftp` is created the first time the container is started and contains default files. Modify these files with your information and restart the container.**

Manage the container using a web browser. Navigate to the IP address of the container and one of the `HTTPPORT`s.

**NOTE: Network interface must be UP i.e. a cable plugged in.**

Example `docker run` and `docker compose` commands as well as sample commands to create the macvlan are below.


## Features

- Ubuntu base image
- Plus:
  - bsdmainutils
  - ftp
  - fzf
  - iproute2
  - iputils-ping
  - isc-dhcp-server
  - python3-minimal
  - rsyslog
  - tftp-hpa
  - tftpd-hpa
  - tmux
  - tzdata
  - vsftpd
  - webfs
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


## Sample commands to create the `macvlan`

Create the docker macvlan interface.

```bash
docker network create -d macvlan --subnet=172.21.0.0/16 --gateway=172.21.255.254 \
    --aux-address="mgmt_ip=172.21.255.253" -o parent="eth0" \
    --attachable "ztp01"
```

Create a management macvlan interface.

```bash
sudo ip link add "ztp01" link "eth0" type macvlan mode bridge
sudo ip link set "ztp01" up
```

Assign an IP on the management macvlan interface plus add routes to the docker container.

```bash
sudo ip addr add "172.21.255.253/32" dev "ztp01"
sudo ip route add "172.21.0.0/16" dev "ztp01"
```

## Sample `docker run` command

```bash
docker run -dit \
    --name "ztp01" \
    --network "ztp01" \
    --ip "172.21.255.252" \
    -h "ztp01" \
    -v "${PWD}/ftp:/opt/ztp/ftp" \
    -e TZ="UTC" \
    -e MGMTIP="172.21.255.253" \
    -e GATEWAY="172.21.255.254" \
    -e HUID="1000" \
    -e HGID="1000" \
    -e HTTPPORT1="8080" \
    -e HTTPPORT2="8081" \
    -e HTTPPORT3="8082" \
    -e HTTPPORT4="8083" \
    -e HOSTNAME="ztp01" \
    -e APPNAME="ztp" \
    "toddwint/ztp"
```


## Sample `docker compose` (`compose.yaml`) file

```yaml
name: ztp01

services:
  ztp:
    image: toddwint/ztp
    hostname: ztp01
    ports:
        - "172.21.255.252:8080:8080"
        - "172.21.255.252:8081:8081"
        - "172.21.255.252:8082:8082"
        - "172.21.255.252:8083:8083"
    networks:
        default:
            ipv4_address: 172.21.255.252
    environment:
        - HUID=1000
        - HGID=1000
        - HOSTNAME=ztp01
        - TZ=UTC
        - MGMTIP=172.21.255.253
        - GATEWAY=172.21.255.254
        - HTTPPORT1=8080
        - HTTPPORT2=8081
        - HTTPPORT3=8082
        - HTTPPORT4=8083
    privileged: true
    cap_add:
      - NET_ADMIN
    volumes:
      - "${PWD}/ftp:/opt/ztp/ftp"
    tty: true

networks:
    default:
        name: "ztp01"
        external: true
```
