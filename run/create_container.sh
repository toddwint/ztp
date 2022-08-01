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
