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
- Download the image and start a new container. The folder `ftp` will be created as specified in the `create_container.sh` script.
- An example CSV file should be found in `ftp`
- Fill in the file `ftp/ztp.csv` with a list of device hardware models, MACs, os image names, and configuration file names.
- Modify it as you need and place it back in the same folder with the same name.
- You can use the `csv_filter.py` or `csv_filter.sh` to create CSV files sorted by vendor or model and rename them to `ztp.csv` as needed.
- Transfer the configuration files and os images to `ftp/os_images` and `ftp/config_files`.
- Trigger the container to update by restarting it with `./restart.sh`, `./stop.sh` and `./start.sh`, or run `./exec/generate_dhcp_conf.sh`
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
SUBNET=172.21.0.0/16
GATEWAY=172.21.255.254
HTTPPORT=8080
HOSTNAME=ztpsrvr01
```

## Sample docker create container command

```
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
```

## Sample webadmin.html.template file

See my github page (referenced above).


## Login page

Open the `webadmin.html` file.

Or just type in your browser `http://<ip_address>:<port>` or `http://<ip_address>:<(port+1)>`


## Description of scripts

### Files in `build` directory

Files and subdirectories in `build` are used to create the docker image.

A user can clone the project as modify these files as needed to create their own image.


### Files in `run` directory

These are files used to manage the docker container. Create it, delete it, start, and stop it.

- config.txt
    - User defined variables for the container instance.
- create_container.sh
    - Creates a networking interface, creates a container, and the webadmin.html file.
- delete_container.sh
    - Remove the networking interfaces, deletes the container.
- is_running.sh
    - Displays a message whether the container is running or not.
- restart.sh
    - Restarts the running container. Useful when modifying the ztp.csv file.
- rm_ftp_dir.sh
    - Removes the container volume if for some reason the user wants to start fresh.
- start.sh
    - Starts the container. Useful when modifying the ztp.csv file or running the container at a later time.
- stop.sh
    - Stops the container. Useful when modifying the ztp.csv file or running the container at a later time.
- webadmin.html.template
    - A template webadmin file that is updated with the IP and PORT of the container when it is created.
- webadmin.md
    - A template webadmin file used to create webadmin.html.template.


### Files in `run/exec` directory

These are files used to debug and manage the container while running.

- exec/dhcp_lease_list.sh
    - Shows the dhcp leases of unspecified hosts.
- exec/ftp_process_status.sh
    - Shows the ftp system processes and can show active transfers.
- exec/generate_dhcp_conf.sh
  - Run this to regenerate the DHCP server config and restart services after the ztp.csv file is updated.
- exec/kill_frontail.sh
    - Stops frontail.
- exec/kill_tailon.sh
    - Stops tailon.
- exec/processes_status.sh
    - Shows the processes running on the container.
- exec/restart_dhcpd.sh
    - Restarts the DHCP server on the container.
- exec/restart_frontail.sh
    - Stops and starts frontail.
- exec/restart_tailon.sh
    - Stops and starts tailon.
- exec/restart_tftpd-hpa.sh
    - Restarts the TFTP server on the container.
- exec/restart_vsftpd.sh
    - Restarts the FTP server on the container.
- exec/run_frontail.sh
    - Starts frontail.
- exec/run_tailon.sh
    - Starts tailon.
- exec/services_status.sh
    - Shows the status of the services isc-dhcp-server, vsftpd, tftpd-hpa, frontail, and tailon.
- exec/show_ip_addr.sh
    - Shows the IP address of the container.
- exec/sockets_status.sh
    - Shows the active sockets on the container.
- exec/tail_syslog.sh
    - Alternatively to webadmin.html, this can show the DHCP/FTP/TFTP logs on the container.
- exec/view_dhcpd_conf.sh
    - Print the contents of `dhcpd.conf` to the terminal.
- exec/view_tftpd-hpa_conf.sh
    - Print the contents of `tftpd-hpa` to the terminal.
- exec/view_vsftpd_conf.sh
    - Print the contents of `vsftpd.conf` to the terminal.
- exec/view_ztp_csv.sh
    - Print the contents of `ztp.csv` to the terminal.


## Issues?

Make sure if you set the correct interface name and an IP is not needed. Delete the container and try again if your adapter was not specified correctly.
