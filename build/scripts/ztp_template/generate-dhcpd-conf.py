#!/usr/bin/env python3
#!python3
'''
 Input a CSV that has the Hardware,MAC,OS,Config and output a modified 
 dhcpd.conf file based upon the template.
 Script will replace the dhcpd, tftp, and ftp configuration files,
 and then restart the processes.
'''
__version__ = '0.0.5'

import argparse
import csv
import ipaddress
import os
import pathlib
import re
import subprocess

import mactools # mactools.py in same dir

# Variable Definitions
#starting_ip_addr = '192.168.10.2'
file_server = '192.168.10.1'
gateway = '192.168.10.254'
csv_filename = 'ztp.csv'
csv_path = pathlib.Path('/opt/ztp/scripts/ftp')
ftpd_daemon_name = 'vsftpd'
tftpd_daemon_name = 'tftpd-hpa'
dhcpd_daemon_name = 'isc-dhcp-server'
ftpd_template = 'vsftpd.conf.template'
tftpd_template = 'tftpd-hpa.template'
dhcpd_template = 'dhcpd.conf.template'
ftpd_tmp_config_file = 'vsftpd.conf'
tftpd_tmp_config_file = 'tftpd-hpa'
dhcpd_tmp_config_file = 'dhcpd.conf'
ftpd_config_file_loc = '/etc/vsftpd.conf'
tftpd_config_file_loc = '/etc/default/tftpd-hpa'
dhcpd_config_file_loc = '/etc/dhcp/dhcpd.conf'
# ftpd_root_native_path and tftpd_root_native_path use current dir
# as the base path.
# DO NOT PUT A LEADING SLASH '/' character inside the quotes.
# A trailing slash is ok.
ftpd_root_native_path = pathlib.Path('/opt/ztp/scripts/').resolve() / 'ftp'  # *see note above
tftpd_root_native_path = pathlib.Path('/opt/ztp/scripts/').resolve() / 'ftp' # *see note above
ftp_os_image_virtual_path = '/os_images/' 
ftp_config_file_virtual_path = '/config_files/' 
tftp_os_image_virtual_path = '/os_images/' 
tftp_config_file_virtual_path = '/config_files/' 
transfer_mode = 'ftp'
ftp_timeout = '3600'
columns = ['hardware', 'mac', 'os', 'config']
model_vendor = {
        'srx345': 'juniper', 
        'srx1500': 'juniper', 
        '2930f': 'aruba'
        }
increment_mac_list = ['srx345']
client_templates = {
        'juniper': '''
host {hostname} {{
    hardware ethernet {macaddr};
    fixed-address {ip_addr};
    #option tftp-server-name "{file_server}";
    option ztp.juniper-ftp-timeout "{ftp_timeout}";
    option ztp.juniper-transfer-mode {transfer_mode};
    option ztp.juniper-image-file-name "{ftp_os_image}";
    option ztp.juniper-config-file-name "{ftp_config_file}";
}}
''',
        'aruba': '''
host {hostname} {{
    hardware ethernet {macaddr};
    fixed-address {ip_addr};
    #option tftp-server-name "{file_server}";
    option ztp.aruba-image-file-name "{tftp_os_image}";
    option ztp.aruba-config-file-name "{tftp_config_file}";
}}
'''
}

# Create command line arguments (optionally to get a different filename)
parser = argparse.ArgumentParser(
    description='Generate dhcpd.conf file from CSV file.',
    epilog='If you need more help, tough.',
    )
parser.add_argument(
    '-v', '--version',
    help='show the version number and exit',
    action='version',
    version=f'Version: {__version__}',
    )
parser.add_argument(
    'filename',
    nargs='?',
    type=pathlib.Path,
    default=csv_filename,
    help=f'name of CSV file (default={csv_filename})',
    )
args = parser.parse_args()

csv_filename = csv_path / args.filename
ip_addr = ipaddress.IPv4Address(file_server) + 1
gateway = ipaddress.IPv4Address(gateway)
ftpd_template = pathlib.Path(ftpd_template)
tftpd_template = pathlib.Path(tftpd_template)
dhcpd_template = pathlib.Path(dhcpd_template)
ftpd_tmp_config_file = pathlib.Path(ftpd_tmp_config_file)
tftpd_tmp_config_file = pathlib.Path(tftpd_tmp_config_file)
dhcpd_tmp_config_file = pathlib.Path(dhcpd_tmp_config_file)
ftp_os_image_virtual_path = pathlib.Path(ftp_os_image_virtual_path.lstrip('/'))
ftp_config_file_virtual_path = pathlib.Path(ftp_config_file_virtual_path.lstrip('/'))
tftp_os_image_virtual_path = pathlib.Path(tftp_os_image_virtual_path.lstrip('/'))
tftp_config_file_virtual_path = pathlib.Path(tftp_config_file_virtual_path.lstrip('/'))

# Make working copies of template files which will be modified
print(f'Making `{ftpd_tmp_config_file}` from `{ftpd_template}`')
print(f'Making `{tftpd_tmp_config_file}` from `{tftpd_template}`')
print(f'Making `{dhcpd_tmp_config_file}` from `{dhcpd_template}`')
ftpd_tmp_config_file.write_text(ftpd_template.read_text())
tftpd_tmp_config_file.write_text(tftpd_template.read_text())
dhcpd_tmp_config_file.write_text(dhcpd_template.read_text())


# Read the CSV file, store it, get the headers, and close the file 
with open(csv_filename) as f:
    t = f.readlines()
reader_dict = csv.DictReader(t)
columns_dict = {k:v for k,v in zip(columns, reader_dict.fieldnames)}

# Do all the magic to the dhcpd file from the CSV information
print('Creating new dhcpd.conf file from csv...')
for n,row in enumerate(reader_dict, start=1):
    hardware = row[columns_dict['hardware']]
    if not any(
            (model := x) for x in model_vendor 
            if x in re.sub('[ :.-]', '', hardware.lower())
            ):
        print(f"Model `{hardware}` not found")
        continue
    hostname = f'{model_vendor[model]}{n:03d}'
    os_image = row[columns_dict['os']].strip()
    config_file = row[columns_dict['config']].strip()
    if gateway == ip_addr:
        ip_addr += 1
    if model in increment_mac_list:
        macaddr = mactools.incr_mac(row[columns_dict['mac']])
    else:
        macaddr = mactools.convert_to_str(row[columns_dict['mac']])
    output = client_templates
    if not os_image:
        output = {
                key:re.sub('.*os_image.*\n', '', template)
                for key, template in output.items()
                }
    if not config_file:
        output = {
                key:re.sub('.*config_file.*\n', '', template)
                for key, template in output.items()
                }
    ftp_os_image = '/' / ftp_os_image_virtual_path / os_image
    ftp_config_file = '/' / ftp_config_file_virtual_path / config_file
    tftp_os_image = '/' / tftp_os_image_virtual_path / os_image
    tftp_config_file = '/' / tftp_config_file_virtual_path / config_file
    output = output[model_vendor[model]].format_map(vars())
    with open('dhcpd.conf', mode='a') as f:
        f.write(output)
    ip_addr += 1

# Modify the FTP/TFTP working templates with path to the os/configs
ftpd_tmp_config_file.write_text(
    re.sub(
        r'(anon_root=|local_root=).*', 
        f'\g<1>{ftpd_root_native_path}', 
        ftpd_tmp_config_file.read_text()
        )
    )
tftpd_tmp_config_file.write_text(
    re.sub(
        r'(TFTP_DIRECTORY=).*', 
        f'\g<1>"{tftpd_root_native_path}"', 
        tftpd_tmp_config_file.read_text()
        )
    )

# Copy working templates to the server daemon locations
print(f'Copying `{ftpd_tmp_config_file}` to `{ftpd_config_file_loc}`')
print(f'Copying `{tftpd_tmp_config_file}` to `{tftpd_config_file_loc}`')
print(f'Copying `{dhcpd_tmp_config_file}` to `{dhcpd_config_file_loc}`')
subprocess.run(['cp', ftpd_tmp_config_file, ftpd_config_file_loc])
subprocess.run(['cp', tftpd_tmp_config_file, tftpd_config_file_loc])
subprocess.run(['cp', dhcpd_tmp_config_file, dhcpd_config_file_loc])

# Set permissions of templates in ztp folder back to host user
subprocess.run([
    'chown', 
    f"{os.environ['HUID']}:{os.environ['HGID']}", 
    dhcpd_tmp_config_file,
    ftpd_tmp_config_file, 
    tftpd_tmp_config_file, 
    ])

# Set the permissions of the tftp and ftp folders
subprocess.run(['chmod', '755', '-R', ftpd_root_native_path])
#subprocess.run(['chown', 'root:ftp', '-R', ftpd_root_native_path])
subprocess.run(['chmod', '755', '-R', tftpd_root_native_path])
#subprocess.run(['chown', 'root:tftp', '-R', tftpd_root_native_path])
print(f'Permissions set for folders `{ftpd_root_native_path}` and `{tftpd_root_native_path}`')

# Restart FTP server daemon
subprocess.run(['service', ftpd_daemon_name, 'restart'])
subprocess.run(['service', ftpd_daemon_name, 'status'])

# Restart TFTP server daemon
subprocess.run(['service', tftpd_daemon_name, 'restart'])
subprocess.run(['service', tftpd_daemon_name, 'status'])

# Restart DHCP server daemon
# delete old pid first
subprocess.run(['rm', '/var/run/dhcpd.pid'])
subprocess.run(['service', dhcpd_daemon_name, 'restart'])
subprocess.run(['service', dhcpd_daemon_name, 'status'])

# Show DHCP leases for non-host entries
print('Entries below were not found in a host scope in the DHCP file.')
subprocess.run('dhcp-lease-list')

# Start Frontail to monitor the ZTP server
print(f'Running command `./stop_frontail.sh`')
subprocess.run('./stop_frontail.sh')
print(f'Running command `./start_frontail.sh`')
subprocess.run('./start_frontail.sh')
print(f"Open your browser to `http://{file_server}:{os.environ['HTTPPORT']}`")

# Start Tailon to monitor the ZTP server
print(f'Running command `./stop_tailon.sh`')
subprocess.run('./stop_tailon.sh')
print(f'Running command `./start_tailon.sh`')
subprocess.run('./start_tailon.sh')
print(f"Open your browser to `http://{file_server}:{int(os.environ['HTTPPORT'])+1}`")

