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
- Download the image and start a new container. The folder `run/ztp` will be created.
- Fill in the file `run/ztp/ztp.csv` with a list of device hardware models, MACs, os image names, and configuration file names.
- An example CSV file should be found in `run/ztp`
- Modify it as you need and place it back in the same folder with the same name.
- Transfer the configuration files and os images to `run/ztp/ftp/os_images` and `run/ztp/ftp/config_files`.
- Trigger the container to update by restarting it with `stop.sh` and `start.sh` or run `generate_dhcp_conf.sh`
- Open the file webadmin.html to:
    - View DHCP/FTP/TFTP messages in a web browser ([frontail](https://github.com/mthenw/frontail))
        - tail the file
        - pause the flow
        - search through the flow
        - highlight multiple rows
    - Alternatively, view the DHCP/FTP/TFTP messages and configuration files in a web browser ([tailon](https://github.com/gvalkov/tailon))


## Sample `config.txt` file

```
TZ=America/Chicago
INTERFACE=eth0
SUBNET=192.168.0.0/16
GATEWAY=192.168.0.1
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
cp webadmin.html.template webadmin.html
sed -Ei 's/\bIPADDR:HTTPPORT\b/'"$IP"':'"$HTTPPORT"'/g' webadmin.html
sed -Ei 's/\bIPADDR:HTTPPORTPLUSONE\b/'"$IP"':'"$(expr $HTTPPORT + 1)"'/g' webadmin.html
```

## Sample webadmin.html.template file

See my github page (referenced above).


## Login page

Open the `webadmin.html` file.

Or just type in your browser `http://<ip_address>:<port>` or `http://<ip_address>:<(port+1)>`


## Description of scripts

- config.txt
    - User defined variables for the container instance.
- create_container.sh
    - Creates a networking interface, creates a container, and the webadmin.html file.
- delete_container.sh
    - Remove the networking interfaces, deletes the container.
- generate_dhcp_conf.sh
    - Run this to regenerate the DHCP server config and restart services after the ztp.csv file is updated.
- is_running.sh
    - Displays a message whether the container is running or not.
- make_network.sh
    - Creates the networking adapter if for some reason it was not created using the create_container.sh script.
- remove_network.sh
    - Removes the networking adapter if for some reason the user wants to delete it and maybe create it again.
- remove_volume.sh
    - Removes the container volume if for some reason the user wants to start fresh.
- restart_dhcpd.sh
    - Restarts the DHCP server on the container.
- restart_tftpd-hpa.sh
    - Restarts the TFTP server on the container.
- restart_vsftpd.sh
    - Restarts the FTP server on the container.
- show_ip_addr.sh
    - Shows the IP address of the container.
- start.sh
    - Starts the container. Useful when modifying the ztp.csv file or running the container at a later time.
- stop.sh
    - Stops the container. Useful when modifying the ztp.csv file or running the container at a later time.
- tail_syslog.sh
    - Alternatively to webadmin.html, this can show the DHCP/FTP/TFTP logs on the container.
- webadmin.html.template
    - A template webadmin file that is updated with the IP and PORT of the container when it is created.
- webadmin.md
    - A template webadmin file used to create webadmin.html.template.

## Issues?

Make sure if you set the correct interface name and an IP is not needed.
