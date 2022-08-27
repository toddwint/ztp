#!/usr/bin/env bash
source "$(dirname "$(realpath $0)")"/config.txt
HUID=$(id -u)
HGID=$(id -g)

# Make the macvlan needed to do DHCP
docker network create -d macvlan --subnet="$SUBNET" --gateway="$GATEWAY" -o parent="$INTERFACE" "$HOSTNAME"-br
sudo ip link add "$HOSTNAME"-net link "$INTERFACE" type macvlan mode bridge
sudo ip addr add "$GATEWAY"/32 dev "$HOSTNAME"-net
sudo ip link set "$HOSTNAME"-net up
sudo ip route add "$SUBNET" dev "$HOSTNAME"-net

# Volume can be changed to another folder. For Example:
# -v /home/"$USER"/Desktop/"$HOSTNAME":/opt/ztp/scripts/ftp \
docker run -dit \
    --name "$HOSTNAME" \
    --network "$HOSTNAME"-br \
    -h "$HOSTNAME" \
    -v "$(pwd)"/ftp:/opt/ztp/scripts/ftp \
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
cp webadmin.html.template webadmin.html
sed -Ei 's/\bIPADDR:HTTPPORT\b/'"$IP"':'"$HTTPPORT"'/g' webadmin.html
sed -Ei 's/\bIPADDR:HTTPPORTPLUSONE\b/'"$IP"':'"$(expr $HTTPPORT + 1)"'/g' webadmin.html
