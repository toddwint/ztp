---
title: ZTP Instructions
author: Todd Wintermute
date: 2025-11-09
---


# Overview


## What is ZTP

ZTP stands for Zero-Touch Provisioning. It is a way of provisioning telecommunications devices without the need of manual intervention.


## What is this software package?

This tool is a Docker image and set of GitHub files.

The Docker image contains a server application which can be used in two different methods to provision devices including update the Operating System and/or load a configuration file.

The GitHub files contain scripts used to make managing the Docker image easier as well as the source code of the Docker image.


## Who is this for?

This tool if for anyone who has a need to update the operating system and/or load a configuration on a factory default Juniper or Aruba networking device.


## What PC platforms are supported?

This ZTP Docker image is designed to work using a Linux operating system. Specifically, it was designed and tested on Ubuntu 22.04 Jammy Jellyfish.

It is also required to install `Docker`. It is recommended to have `Git` installed, but not required. On many Linux systems `Git` is already installed. For instructions on installing Docker, please see the section [Install Docker](#install-docker).

The reason Windows and MacOS are not supported is because this application makes use of the Docker `MACVLAN` network feature which Docker only supports on Linux. If you would like to try to get it to work on Windows or MacOS, you might have some success using Docker `host networking`. For more information about the different types of Docker network drivers see this [Docker page](https://docs.docker.com/network/drivers/). Another option is running a Linux Virtual Machine on these platforms. See the section [Running inside a Virtual Machine](#running-inside-a-virtual-machine)


## How does it work?

First, the device vendor has to include the option for provisioning their devices via ZTP. Juniper and Aruba do. So do other vendors like Cisco, but this tool only includes the DHCP options and code for Juniper and Aruba.

When the ZTP capable device boots up from a factory default configuration, it looks for a DHCP message which includes certain options telling it the location of the file server and the file names it needs to download. It can also include the transfer protocol to use such as ftp or tftp. It uses these options to download the files. Then it installs these files all by itself.

This Docker image contains a DHCP, FTP, TFTP, and NTP server as well as scripts to put everything together. It contains additional applications and scripts so that you can view the transfers in your web browser and monitor the progress.

Be aware, although a file transfer might be complete, the device might still need 15 or 20 minutes to finish installing.

So it sounds interesting. You want to try it out, but how do you get the information into ZTP? Well, there are two methods...


### Two provisioning methods

This tool supports two different methods to provision devices.

1. DHCP Vendor Class Identifiers
    - `vendor_class_defaults.csv`
2. MAC addresses
    - `ztp.csv`

Samples of each of these files are created and put in the `ftp` folder/volume the first time the container is started.


#### Provisioning method 1: Vendor Class Identifier

Devices send a vendor class identifier string in DHCP requests to the DHCP server. This string can be used to provide the OS and/or configuration file to that specific type of device.

This option is a good idea if you want to load the same OS and/or a starting configuration to many of the same device types.

On Aruba devices you can obtain this string with the command `show dhcp client vendor-specific`.

On Juniper devices, a zeroized device or device with factory defaults should have this string listed in the configuration under the interfaces section on the interfaces configured for DHCP.

To use this method, fill out the information in `vendor_class_defaults.csv`


##### Vendor Class ID file: `vendor_class_defaults.csv`

A default file is created and put in the `ftp` folder/volume the first time the container is started.

You can edit it using a text editor or using a program like Microsoft Excel or LibreOffice Calc. Just remember to save it as a CSV file as it might prompt you to save it in a different format.

Here is a look at the example `vendor_class_defaults.csv`:
```csv
hardware,vendor_class_string,os,config
srx345,Juniper-srx345,,
srx1500,Juniper-srx1500,,
2930f,Aruba JL253A 2930F-24G-4SFP+ Switch dslforum.org,,
2930f,Aruba JL254A 2930F-48G-4SFP+ Switch dslforum.org,,
2930f,Aruba JL255A 2930F-24G-PoE+-4SFP+ Switch dslforum.org,,
2930f,Aruba JL256A 2930F-48G-PoE+-4SFP+ Switch dslforum.org,,
2930f,Aruba JL260A 2930F-48G-4SFP Switch dslforum.org,,
2930f,Aruba JL263A 2930F-24G-PoE+-4SFP+-TAA Switch dslforum.org,,
2930f,Aruba JL264A 2930F-48G-PoE+-4SFP+-TAA Switch dslforum.org,,
```

Or in an human viewable way

| hardware | vendor_class_string                                       | os  | config |
|---------:|:----------------------------------------------------------|:----|:-------|
| srx345   | Juniper-srx345                                            |     |        |
| srx1500  | Juniper-srx1500                                           |     |        |
| 2930f    | Aruba JL253A 2930F-24G-4SFP+ Switch dslforum.org          |     |        |
| 2930f    | Aruba JL254A 2930F-48G-4SFP+ Switch dslforum.org          |     |        |
| 2930f    | Aruba JL255A 2930F-24G-PoE+-4SFP+ Switch dslforum.org     |     |        |
| 2930f    | Aruba JL256A 2930F-48G-PoE+-4SFP+ Switch dslforum.org     |     |        |
| 2930f    | Aruba JL260A 2930F-48G-4SFP Switch dslforum.org           |     |        |
| 2930f    | Aruba JL263A 2930F-24G-PoE+-4SFP+-TAA Switch dslforum.org |     |        |
| 2930f    | Aruba JL264A 2930F-48G-PoE+-4SFP+-TAA Switch dslforum.org |     |        |

And here is a description of each column:

- hardware
    - A unique string that identifies the specific make and model of the device. This string is used to determine whether the device is Juniper or Aruba and use the appropriate DHCP option codes as well as the transfer protocol for the device i.e. ftp or tftp.
- vendor_class_string
    - The vendor-id the device(s) will provide to the DHCP server in a DHCP request.
- os_image
    - The operating system file for the device(s). Junipers usually use `.tgz` and Aruba usually uses `.swi` files.
- config_file
    - The configuration file for the device(s). Note that Aruba devices must include a specific string in the header as well as the correct module. Also, Aruba LAN switches will continue to perform ZTP on themselves unless the following commands are added to the configuration file: `no dhcp config-file-update` and `no dhcp image-file-update`


#### Provisioning method 2: MAC addresses

The device's MAC address is a unique identifier which can be used to provide the OS and/or configuration file to that specific device.

This option is a good idea if you want to load a specific configuration and OS per device.

The MAC addresses can be obtained from the rear sticker on the device. An affordable Bluetooth barcode scanner from Amazon.com and a Google Sheet open on your phone can be very handy in making this task a lot easier. Another good option is using a smartphone barcode scanner application.

To use this method, fill out the information in `ztp.csv`.


##### MAC method file: `ztp.csv`

A default file is created and put in the `ftp` folder/volume the first time the container is started.

You can edit it using a text editor or using a program like Microsoft Excel or LibreOffice Calc. Just remember to save it as a CSV file as it might prompt you to save it in a different format.

Here is a look at the example `ztp.csv`:
```csv
hardware,mac,os,config
2930f,888888eeeee1,aruba-2930f.swi,switch1.cfg
ex2300,888888eeeee2,junos-ex2300.tgz,switch2.cfg
ex4100,888888eeeee3,junos-ex4100.tgz,switch3.cfg
srx1500,888888eeeee4,junos-srx1500.tgz,router1.cfg
srx345,888888eeeee5,junos-srx345.tgz,router2.cfg
acx7024,888888eeeee6,junos-acx7024.tgz,router3.cfg
```

Or in an human viewable way


| hardware | mac          | os                | config      |
|:---------|:-------------|:------------------|:------------|
| 2930f    | 888888eeeee1 | aruba-2930f.swi   | switch1.cfg |
| ex2300   | 888888eeeee2 | junos-ex2300.tgz  | switch2.cfg |
| ex4100   | 888888eeeee3 | junos-ex4100.tgz  | switch3.cfg |
| srx1500  | 888888eeeee4 | junos-srx1500.tgz | router1.cfg |
| srx345   | 888888eeeee5 | junos-srx345.tgz  | router2.cfg |
| acx7024  | 888888eeeee6 | junos-acx7024.tgz | router3.cfg |

And here is a description of each column:

- hardware
    - A unique string that identifies the specific make and model of the device. This string is used to determine whether the device is Juniper or Aruba and use the appropriate DHCP option codes as well as the transfer protocol for the device i.e. ftp or tftp.
- mac
    - The MAC address of the device. Specifically the MAC obtained from the rear sticker. This tool includes an increment amount for some devices to increment the base MAC of the device and configure the DHCP server for the MAC address of the first port on the device.
- os_image
    - The operating system file for the device(s). Junipers usually use `.tgz` and Aruba usually uses `.swi` files.
- config_file
    - The configuration file for the device(s). Note that Aruba devices must include a specific string in the header as well as the correct module. Also, Aruba LAN switches will continue to perform ZTP on themselves unless the following commands are added to the configuration file: `no dhcp config-file-update` and `no dhcp image-file-update`


#### How to specify which provisioning method you want to use

Both methods will be checked when the application starts, and they can both be used at the same time.

There is a default precedence to choose the more specific entry over the more generic ones. That means if you specify a configuration file using the MAC method and the Vendor Class method, the file listed in the MAC method (`ztp.csv`) will be loaded to the device.

If you only want to use one method, do not specify the OS file, configuration file, etc. in the other file and it will not be used.


### Supported devices

Currently only Juniper and Aruba are supported.

Not all Juniper and Aruba devices are supported either.

The supported device models are :

1. Aruba 2930F LAN switches
    - JL253A
    - JL254A
    - JL255A
    - JL256A
    - JL260A
    - JL263A
    - JL264A
2. Juniper SRX345
3. Juniper SRX1500
4. Juniper AXC7024
5. Juniper EX2300
6. Juniper EX4100


### Expanding the devices supported

If your device is not in the list, it still might be possible to use this tool on it.

However, only DHCP codes for Juniper and Aruba are supported by this tool.


#### Viewing supported devices or expanding the list: `supported_device_models.json`

You can view the currently supported devices by opening the file `supported_device_models.json`

It looks like this:

```json
{
 "srx345": {
  "vendor": "juniper",
  "incr_mac": 1
 },
 "srx1500": {
  "vendor": "juniper",
  "incr_mac": null
 },
 "acx7024": {
  "vendor": "juniper",
  "incr_mac": 1023
 },
 "2930f": {
  "vendor": "aruba",
  "incr_mac": null
 },
 "ex2300": {
  "vendor": "juniper",
  "incr_mac": null
 },
 "ex4100": {
  "vendor": "juniper",
  "incr_mac": null
 }
}

```

If you have a Juniper or Aruba device not in the list, you can try adding it to the list. Chances are it will work.

Make sure to add the item in correct `json` format including the comma after the previous entry's `}` (close curly brace).

Let's look at one entry and explain what the fields do.

```json
 "srx345": {
  "vendor": "juniper",
  "incr_mac": 1
 },
```

- "srx345"
    - The unique model for the device. Use this value in the `hardware` column in `ztp.csv` and `vendor_class_defaults.csv`.
- "vendor": "juniper"
    - Choices are either `juniper` or `aruba`. Tells the application which DHCP codes to use and which transfer protocol to use (ftp vs tftp).
- "incr_mac": 1
    - Tells the application if it needs to increment the MAC address entered (usually scanned from the rear sticker) for the specific Ethernet port on the device being used.
        - On Juniper srx345 this means enter the MAC from the sticker on the back and use port `ge-0/0/0`.


### Where to plug in the cables

Use the following ports on the devices when connecting to the ZTP application.

1. Aruba 2930F LAN switches
    - any port
2. Juniper SRX345
    - `ge-0/0/0`
3. Juniper SRX1500
    - `ge-0/0/0`
4. Juniper AXC7024
    - `MGMT` port
5. Juniper EX2300
    - any port
6. Juniper EX4100
    - any port


### Files and folders inside the `ftp` folder/volume

- vendor_class_defaults.csv
    - See [Provisioning method 1: Vendor Class Identifier](#provisioning-method-1-vendor-class-identifier)
- ztp.csv
    - See [Provisioning method 2: MAC addresses](#provisioning-method-2-mac-addresses)
- supported_device_models.json
    - See [Expanding the devices supported](#expanding-the-devices-supported)
- csv_filter.py
    - A python script which can be used to create additional CSV files filtered by make and model. Run `csv_filter.py -h` for more info.
- os_images/
    - The folder where the operating system files should be placed.
- config_files/
    - The folder where the configuration files should be placed.
- .exists
    - This file is added automatically and tells ZTP not to override the files inside the `ftp` folder. Erase this file and restart the container to receive a fresh copy of all the files.


# Running ZTP


## Install the requirements

### Install Docker

On a Linux computer, install Docker.

If you are using Ubuntu Linux, follow these instructions:

[Docker.com: Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

To run Docker without requiring root, follow the following instructions:

[Docker.com: Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

_These steps can also be found in this document near the end in [Installing Docker on Ubuntu Linux](#installing-docker-on-ubuntu-linux)_


### Install git (optional, but recommended)

Git is usually already installed.

For instructions for specific platforms, see GitHub's page on installing git: [GitHub.com: Install Git](https://github.com/git-guides/install-git).

For Ubuntu, see the section [Install git on Ubuntu Linux](#install-git-on-ubuntu-linux)


## Download the files

The Docker image contains everything to run the application.

Download the Docker image with the following command:

```bash
docker pull toddwint/ztp
```

To verify the image has downloaded please view the section [Download the ZTP Docker image](#download-the-ztp-docker-image).


The GitHub files are optional, but recommended as it makes it easier to run and manage.

Download the GitHub project to the current folder with the following command:

```bash
git clone https://github.com/toddwint/ztp
```

There are three main folders in the GitHub project. Here is a brief description:

- build
    - Contains the source code and Docker files which is everything you need if you want to build the application offline.
    - You are also free to modify the code and tailor it to your own needs.
    - Most users won't need these files. They can be discarded.
- compose
    - Contains files to assist in creating and managing the container.
    - Uses docker compose, a tool which can run multi-container applications.
    - I recommend renaming this folder to the hostname of your ZTP server (as configured in `config.txt`) such as `ztp01` and moving it to a location on your computer which is easy to access.
- run
    - Contains files to assist in creating and managing the container.
    - Uses docker run, a tool which can only launch a single container application.
    - I recommend using the compose tool over this run tool. However, if you have issues with compose, this is an option.


NOTE: If you do not require the `ztp/build` folder and files, I recommend reorganizing the folder structure as such:

- Rename the `ztp/compose` or `ztp/run` folder (e.g. `ztp01`)
- Remove the unused directory of the two `ztp/run` or `ztp/compose`
- Remove the directory `ztp/build`
- Create a docs folder and copy the `README` and `ZTP Instructions` files to it.

For example commands, see the section [Download the GitHub files](#download-the-github-files).

## Create the Docker container

All the files from here on will be found in the `compose` or `run` folder.


### Modify container configuration parameters: `config.txt`

Before creating the container, it is important to review the default settings in `config.txt`. Each option has a description above it. Most of the defaults should be fine.

You will probably want to update the timezone. This will make the syslog messages match your local timezone. That section looks like this:

```
# To get a list of timezones view the files in `/usr/share/zoneinfo`
TZ=UTC
```

As an example, for my location I enter `America/Chicago`.

The most important variable is `INTERFACE`. Record the name of your Ethernet adapter in Linux and change the variable in this section:

```
# The interface on which to set the IP. Run `ip -br a` to see a list
INTERFACE=eth0
```

**NOTE:** The script will take care of setting the IP address on your Ethernet adapter so that you can communicate with the Docker container. It is not recommended to set an IP on your Ethernet adapter, and it can actually cause issues.


### Run the script to create the container: `create_project.sh` or `create_container.sh`

After configuring the options in `config.txt`, you are ready to create the container.

To create the container run the following command:

`ztp/compose`
```bash
./create_project.sh
```

`ztp/run`
```bash
./create_container.sh
```

The script does a few things more than just create the container. It sets up some environmental variables and loads the parameter in `config.txt` so that those parameters can be passed to the container and also uses those parameters to create a new `MACVLAN` network adapter on your computer. Then it creates the container. Finally it creates an HTML launch page for the application by modifying a template and prompts the user to open this HTML file.

At this point, the ZTP Docker image you downloaded is now a Docker container instance. Also, the folder `ftp` should exist which is the Docker volume for this container.

Inside of the newly created `ftp` folder, you should see the files as explained already in [Files and folders inside the `ftp` folder/volume](#files-and-folders-inside-the-ftp-foldervolume). Modify these files with your information.

Don't forget to copy your OS and configuration files for your devices to `ftp/os_images/` and `ftp/config_files/`


### Transfer files to the ftp folder

Now that the `ftp` folder exists, it is a good time to transfer your files.

You can copy and paste them over if they are on the same machine or if you have a USB drive.

If you have SSH access to the host machine, that might be another good option.

Another option is to use the `FTP` server built inside of ZTP to copy the files over.

Plug a network cable from the PC to PC. ZTP should provide a network address to the other PC. The IP address will match the range specified in config.txt (default=172.21.0.0/16).

Use the following values to connect to the `FTP` server:

- Address or Hostname: `172.21.255.252` (or `IPADDR` value in `config.txt`)
- Username: `ztp` (or `APPNAME` value in `config.txt`)
- Password: `ztp` (or `APPNAME` value in `config.txt`)

__Note: If you are logged in as root directly, the username will be root and the password will be the same as above.__

__Note: If you are using `sudo` to launch the container, the SUDO_UID and SUDO_GID will be used instead of the ids for root.__

Once you have modified your provisioning files and copied the OS and/or configuration files for your devices to the appropriate folders, it is time to see it work.


## Restart the container

Now that we have everything set up for our devices, it is time to restart the container, and let it provision all your devices. ZTP does not automatically detect new files. Restarting will handle this for us.

```bash
./restart.sh
```

The container starts. If the cables are plugged in and your devices powered on with a factory default configuration, it should be provisioning them.


## View the progress

To view the progress, open one of the links in the `webadmin.html` page. This page should have opened by default when you ran `create_project.sh` or `create_container.sh`. If you closed the page or if it never opened, simply click on `webadmin.html`

Inside of the `webadmin.html` launch page, there are several options. Here is a description of each option:

- ttyd
    - A view only page that displays the file transfer report.
- ttyd (w/tmux)
    - An interactive terminal with multiple windows.
        - Window 1 displays the file transfer report.
        - Window 2 displays the log file.
        - Window 3 displays the completed ftp transfers log
        - Window 4 displays the log file filtered for ftp traffic
        - Window 5 displays the log file filtered for tftp traffic
        - Window 6 is access to the terminal.
            - You can run commands from inside the Docker container. Alternatively, you can press `CTRL-C` on any other windows to gain access to the terminal.
            - There are several scripts available in the starting directory (`debug`). Run `ls` to see them. Run them by typing `./` followed by the script name.
- frontail
    - Displays the log file and has filtering capability.
- tailon
    - Displays multiple log files (using the drop down) and also includes filtering capability.
- webfs
    - You can view the files in the `ftp` folder and download them.

You can also interact with the Docker container by using the scripts inside the `exec` folder. Here is a description:

- `bash.sh`
    - Access to the terminal.
        - You can run commands from inside the Docker container. Alternatively, you can press `CTRL-C` on any other windows to gain access to the terminal.
        - There are several scripts available in the starting directory (`debug`). Run `ls` to see them. Run them by typing `./` followed by the script name.
- `tail.sh`
    - Displays the log file.
- `tmux.sh`
    - The same as `ttyd (w/tmux)`, but in the command line instead of the web browser.
- `transfer_report.sh`
    - Displays the file transfer report.


## Stop the container

Hopefully, your devices are loaded now. If not, skip ahead to the section [Common issues](#common-issues).

To stop the container, run this command:

```bash
./stop.sh
```

If you are finished with the container, run this command:

`ztp/compose`
```bash
./delete_project.sh
```

`ztp/run`
```bash
./delete_container.sh
```

Both of these commands will stop the container and copy a timestamped version of the transfer report to your `ftp` folder. Deleting the container will additionally delete the container and remove the networking adapter created with the `create_project.sh` or `create_container.sh` script and the `webadmin.html` file.

Do not be afraid of deleting the container. The files in the `ftp` folder will not be overwritten the next time the container is created as it checks for a `.exists` file inside that folder which is created the first time the container is created. I actually hardly ever use the `stop.sh`, `restart.sh`, or `start.sh` scripts. Instead, I use `create_project.sh` or `create_container.sh` and `delete_project.sh` or `delete_container.sh`.


# Common issues


## Links in `webadmin.html` display the message _"The connection has timed out"_ or _"This Site Can't Be Reached"_

Check that your Ethernet adapter link's status is _UP_ or connect your Ethernet adapter to a network device.

Because of the way `MACVLAN` works, you cannot access the host directly. To work around this, a second `MACVLAN` interface is created on the same Ethernet adapter and a route to the Docker container is added. However, if that physical Ethernet adapter's link status is _DOWN_, then it will not use that adapter. Rather than having a cable plugged in to view the management page, another option is to purchase a USB-to-Ethernet adapter with a built in 4-Port Ethernet switch. See [Running inside a Virtual Machine](#running-inside-a-virtual-machine) for more information.


## You receive errors when running `start.sh`, `restart.sh`, `stop.sh`

This could be because the network no longer exists. Did your computer get restarted? The network adapter won't persist across a reboot.

To resolve this issue, try running `delete_project.sh` or `delete_container.sh` followed by `create_project.sh` or `create_container.sh`


## You receive errors when running `create_project.sh`, `create_container.sh`, `delete_project.sh` or `delete_container.sh`

- Is the name of your Ethernet adapter in `config.txt` correct?
- Do you already have a container running? Run `./is_running.sh` to see.
- Did you change the hostname in `config.txt`? If it differs from the currently running hostname, it won't be able to delete it until you set it back or use Docker commands.


## My Aruba device says _"Connection Refused"_.

Is the OS already at the version you are trying to load?

If so, Aruba LAN switches will try to download the file 5 or 6 times before moving onto the configuration file.


## My device doesn't appear to be loading

- Verify the OS file is for the correct device and the file is not corrupt. Try loading it manually to verify it is correct.
- Verify the configuration file is valid by trying to load it manually.
- Did you create a network storm? Connecting too many switches together can create a network loop where the switch utilization goes to 100% and the network is no longer accessible.
- Did you add the MAC address to the list? Some times new devices get racked, but they don't automatically enter themselves into your files.
- Is the Vendor Class ID string correct?
- Is the device restored to factory defaults?
    - Juniper: `request system zeroize`
    - Aruba: `erase startup-config`
- Verify you are using the correct port on the device. See [Where to plug in the cables](#where-to-plug-in-the-cables)
- If your files contain spaces in their names, try renaming them without spaces.
- Did you specify the full filename including the file extension? If you forgot, the script will search the directory for files with the same name and pick the first one it finds. It also searches for duplicate MAC addresses and configuration files. It will write messages to the log file for all the issues it finds.
- Use the log file to gather more information. See [View the progress](#view-the-progress) for more information about viewing the log file.


# Additional Information


## Links to Docker and GitHub pages

Docker: <https://hub.docker.com/r/toddwint/ztp>

GitHub: <https://github.com/toddwint/ztp>


## Running inside a Virtual Machine

Using a virtual machine is a good way to use this application if you currently run Windows or MacOS.

Configure your networking to `bridge` mode will yield the best results. However, I suggest using a USB-to-Ethernet adapter and attaching it directly to your virtual machine. Even better, _Cable Matters_ makes a USB-to-4-Port-Gigabit-Ethernet-Switch in both standard [USB type A](https://a.co/d/6krs6f4) and [USB type C](https://a.co/d/dCDJ9Oy) connectors. The nice thing about these adapters (other than having 4 Ethernet ports directly connected to your laptop) is that it has an internal switch which means the Ethernet interface will always show link status of _UP_.


## Installing Docker on Ubuntu Linux

Below are the commands taken from Docker's website ([here](https://docs.docker.com/engine/install/ubuntu/) and [here](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)) how to install Docker on Ubuntu Linux.

1. Update the `apt` package index and install packages to allow `apt` to use a repository over HTTPS:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
```

2. Add Docker’s official GPG key:

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

3. Set up the repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) " \
  "signed-by=/etc/apt/keyrings/docker.gpg] " \
  "https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

4. Update the apt package index:

```bash
sudo apt-get update
```

5. Install Docker Engine, containerd, and Docker Compose.

```bash
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-compose-plugin
```

6. Add your user to the `docker` group to manage Docker as a non-root user

```bash
sudo usermod -aG docker $USER
```

7. Log out and log back in so that your group membership is re-evaluated.


## Install git on Ubuntu Linux

Use the following command to install `git` on Ubuntu Linux:

``` bash
sudo apt update
sudo apt install git
```


## Download the ZTP Docker image

Download the Docker image to your Docker image files folder with the following command:

```bash
docker pull toddwint/ztp
```

The docker image downloads to your computer. Verify with the following command:

```bash
docker image ls
```

Example output:
```
REPOSITORY             TAG       IMAGE ID       CREATED         SIZE
toddwint/ztp           latest    dfe47ddf7ccf   5 weeks ago     150MB
```


## Download the GitHub files

Download the GitHub project to the current folder with the following command:

```bash
git clone https://github.com/toddwint/ztp
```

For users that want to run the docker image and never build it from source, the following commands can be used to remove the source files make the directories easier to mange:

`ztp/compose`
```bash
mv ztp/compose/ ztp01
mkdir ztp01/docs
mv ztp/@(README|ZTP Instructions)* ztp01/docs/
rm -rf ztp/
```

`ztp/run`
```bash
mv ztp/run/ ztp01
mkdir ztp01/docs
mv ztp/@(README|ZTP Instructions)* ztp01/docs/
rm -rf ztp/
```


## Give the current user access to `ip` command without requiring a password (optional)

For Ubuntu Linux, add these commands if you do not wish to enter a password when the container starts and creates the network.

```bash
sudo touch /etc/sudoers.d/ip_cmd
sudo chmod 0440 /etc/sudoers.d/ip_cmd
sudo tee /etc/sudoers.d/ip_cmd > /dev/null << EOF
Cmnd_Alias IP_CMD=/usr/sbin/ip,/usr/bin/link,/usr/sbin/route
$USER	ALL=(ALL:ALL) NOPASSWD:IP_CMD
%$USER	ALL=(ALL:ALL) NOPASSWD:IP_CMD
EOF
sudo visudo -c
```


## Updating to a new version

If you wish to download the latest Docker container and GitHub files, perform the following steps:

1. Stop and delete the current container.
    - You can view all the currently running Docker containers by running the command `docker ps` or `docker container ls`

2. Remove the current Docker file image and download the latest one with these commands:
    - You can view all the Docker file images on your system by running the command `docker image ls`

```bash
docker rmi toddwint/ztp
docker pull toddwint/ztp
```

3. Delete the current `ztp` directory, and download the latest ones. Don't forget to copy any important files elsewhere before deleting it. Here are some example commands to do that:

```bash
rm -rf ztp/
git clone https://github.com/toddwint/ztp
```


## Running more than one container at a time.

It is possible to run more than one container at a time. To do so follow these steps.

- Make a copy of the `compose` or `run` folder which I often rename to my container hostname such as `ztp01`.

- In `config.txt` change the Ethernet adapter to a new name (you won't be able to use the same Ethernet adapter) and the hostname. Also, change the IP addresses. I would increment the 2nd octet.


## Changing the default IP scheme

Different size subnets should be fine (/16, /20, /22, etc). Don't put anything smaller than a `/28` network.

The image will reserve the last 4 IPs for the container IP, management host IP, spare IP, and the gateway IP. It will reserve 2 IPs lower than that range for the DHCP range of unknown hosts, but after running the python script will expand that to the IP after your last device.

If you do want to use the first IPs in the subnet range, it should be fine. It will check and skip the static DHCP assignments if those IPs are set.


## Renaming predictable network interface names to user defined values

[Predictable network interface names](https://github.com/systemd/systemd/blob/main/docs/PREDICTABLE_INTERFACE_NAMES.md) look like `ens33`, `eno1`, `enp1s0`, `enx78e7d1ea46da`

If you wish to change this behavior and rename them to names like `lan0` or `lan1`, follow these steps.

**NOTE:** Do not use kernel reserved names like `eth0` or `wlan0`. Those names are reserved. If you run into issues, that is why.

In this example the Ethernet adapter name is: `eno1`. Replace `eno1` with the name of your adapter.

Example: `eno1`

```bash
INTF=eno1
```

Find the pci path of the device. Use `grep` to filter for `ID_PATH` and awk to grab the value.

```bash
udevadm info /sys/class/net/$INTF | grep ID_PATH= | awk -F= '{print $2}'
```

Sample output:

```
pci-0000:03:00.0
```

Save the ID_PATH value to a variable.

```bash
IDPATH=$(udevadm info /sys/class/net/$INTF | grep ID_PATH= | awk -F= '{print $2}')
```

Decide a new name for the interface and save that name to a variable.

Example: `lan1`
```bash
INTFNAME=lan1
```

Run the following command to create the configuration file using the variables created in the previous steps.

```bash
sudo tee /etc/systemd/network/10-${INTFNAME}.link > /dev/null << EOF
[Match]
Path=$IDPATH
[Link]
Name=$INTFNAME
EOF
```

Reboot and verify the names.

Don't see the change? Verify which rule is being used with:

```bash
udevadm info /sys/class/net/eno1
```

If it looks correct, then perform:

```bash
sudo update-initramfs -u
```

Reboot and check again.
