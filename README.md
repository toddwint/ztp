# toddwint/ztp

## Info

<https://hub.docker.com/r/toddwint/ztp>

<https://github.com/toddwint/ztp>

ZTP (Zero-Touch Provisioning) docker image for Juniper SRX345, SRX1500, and HPE Aruba 2930F devices.

This image was created for a specific use case in a specific environment.

## Features

- Performs Zero-Touch Provisioning of
    - Juniper SRX345
    - Juniper SRX1500
    - HPE Aruba 2930F
- Fill in the file `ztp.csv` with a list of device hardware models, MACs, os image names, and configuration file names.
- An example CSV file should be found in `<volume>/ztp`
- Modify it as you need and place it back in the same folder with the same name.
- Transfer the configuration files and os images to `<volume>/ztp/ftp/os_images` and `<volume>/ztp/ftp/config_files`.
- View DHCP/FTP/TFTP messages in a web browser ([frontail](https://github.com/mthenw/frontail))
    - tail the file
    - pause the flow
    - search through the flow
    - highlight multiple rows

## Sample `config.txt` file

```
TZ=UTC
INTERFACE=enx0014d1da21f2
SUBNET=192.168.2.0/24
GATEWAY=192.168.2.254
HTTPPORT=8080
HOSTNAME=ztpsrvr01
```

## Sample docker run command

```
#!/usr/bin/env bash
source config.txt
HUID=$(id -u)
HGID=$(id -g)

# Make the macvlan needed to do DHCP
docker network create -d macvlan --subnet="$SUBNET" --gateway="$GATEWAY" -o parent="$INTERFACE" "$HOSTNAME"-br
sudo ip link add "$HOSTNAME"-net link "$INTERFACE" type macvlan mode bridge
sudo ip addr add "$GATEWAY"/32 dev "$HOSTNAME"-net
sudo ip link set "$HOSTNAME"-net up
sudo ip route add "$SUBNET" dev "$HOSTNAME"-net

docker run -dit \
    --name "$HOSTNAME" \
    --network "$HOSTNAME"-br \
    -h "$HOSTNAME" \
    -p "$IPADDR":"$HTTPPORT":"$HTTPPORT" \
    -v "$(pwd)/ztp":/opt/ztp/scripts/ztp \
    -e TZ="$TZ" \
    -e HTTPPORT="$HTTPPORT" \
    -e HOSTNAME="$HOSTNAME" \
    -e SUBNET="$SUBNET" \
    -e GATEWAY="$GATEWAY" \
    -e HUID="$HUID" \
    -e HGID="$HGID" \
    toddwint/ztp

# Get IP and subnet information and write over template files
IP=$(docker exec "$HOSTNAME" ip addr show eth0 | sed -En 's/^\s+inet\s([0-9.]+).*/\1/p')
NET=$(docker exec "$HOSTNAME" ip addr show eth0 | sed -En 's/^\s+inet\s(([0-9]{,3}.){2}[0-9]{,3}).*/\1/p')
cp template/webadmin.html.template webadmin.html
sed -Ei 's/IPADDR/'"$IP"':'"$HTTPPORT"'/g' webadmin.html
```

## Sample webadmin.html.template file

See my github page (referenced above).


## Login page

Open the `webadmin.html` file.

Or just type in your browser `http://<ip_address>:<port>`


## Issues?

Make sure if you set the correct interface name and an IP is not needed.
