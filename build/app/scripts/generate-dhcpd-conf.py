#!/usr/bin/env python3
#!python3
'''
 Input a CSV that has the Hardware,MAC,OS,Config and output a modified 
 dhcpd.conf file based upon the template.
 Also, generate a dhcp_report.csv file to be used later to monitor
 the progress of the file transfers.
 Script will replace the dhcpd, tftp, and ftp configuration files,
 and then restart the processes.
'''
__version__ = '0.0.8'
__date__ = '2023-06-22'
__author__ = 'Todd Wintermute'

from syslog import syslog
import argparse
import csv
import ipaddress
import json
import os
import pathlib
import re

import mactools # mactools.py in same dir

# Variable Definitions
appname = os.environ['APPNAME']
starting_ip_addr = '192.168.10.1'
file_server = '192.168.1.252'
mgmt_ip_addr = '192.168.1.253'
gateway = '192.168.1.254'
dhcp_start = '192.168.1.249'
dhcp_end = '192.168.1.250'
csv_filename = 'ztp.csv'
csv_path = pathlib.Path(f'/opt/{appname}/ftp')
dhcp_report_template = f'/opt/{appname}/configs/dhcp_report.csv.template'
dhcp_report_template = pathlib.Path(dhcp_report_template)
dhcp_report = f'/opt/{appname}/logs/dhcp_report.csv'
dhcp_report = pathlib.Path(dhcp_report)
dhcpd_daemon_name = 'isc-dhcp-server'
dhcpd_template = f'/opt/{appname}/configs/dhcpd.conf'
dhcpd_tmp_config_file = f'/opt/{appname}/configs/dhcpd.py.conf'
dhcpd_config_file_loc = '/etc/dhcp/dhcpd.conf'
ftpd_root_native_path = pathlib.Path(f'/opt/{appname}/ftp')
tftpd_root_native_path = pathlib.Path(f'/opt/{appname}/ftp')
ftp_os_image_virtual_path = '/os_images/' 
ftp_config_file_virtual_path = '/config_files/' 
tftp_os_image_virtual_path = '/os_images/' 
tftp_config_file_virtual_path = '/config_files/' 
transfer_mode = 'ftp'
ftp_timeout = '3600'
columns = ['hardware', 'mac', 'os', 'config']
device_models_json = f'/opt/{appname}/scripts/device_models.json'
device_models_json = pathlib.Path(device_models_json)
device_models = json.loads(device_models_json.read_text())
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
ip_addr = ipaddress.IPv4Address(starting_ip_addr)
mgmt_ip_addr = ipaddress.IPv4Address(mgmt_ip_addr)
file_server = ipaddress.IPv4Address(file_server)
gateway = ipaddress.IPv4Address(gateway)
dhcp_start = ipaddress.IPv4Address(dhcp_start)
dhcp_end = ipaddress.IPv4Address(dhcp_end)
dhcpd_template = pathlib.Path(dhcpd_template)
dhcpd_tmp_config_file = pathlib.Path(dhcpd_tmp_config_file)
dhcpd_config_file_loc = pathlib.Path(dhcpd_config_file_loc)
ftp_os_image_virtual_path = \
    pathlib.Path(ftp_os_image_virtual_path.lstrip('/'))
ftp_config_file_virtual_path = \
    pathlib.Path(ftp_config_file_virtual_path.lstrip('/'))
tftp_os_image_virtual_path = \
    pathlib.Path(tftp_os_image_virtual_path.lstrip('/'))
tftp_config_file_virtual_path = \
    pathlib.Path(tftp_config_file_virtual_path.lstrip('/'))

# Make working copies of template files which will be modified
print(f'Making `{dhcpd_tmp_config_file}` from `{dhcpd_template}`')
dhcpd_tmp_config_file.write_text(dhcpd_template.read_text())
print(f'Making `{dhcp_report}` from `{dhcp_report_template}`')
dhcp_report.write_text(dhcp_report_template.read_text())

if not csv_filename.exists():
    msg = f'[ERROR] `{csv_filename.name}` was not found. Exiting.'
    print(msg)
    syslog(msg)
    raise(Exception(f'{msg}'))
# Read the CSV file, store it, get the headers, and close the file 
with open(csv_filename) as f:
    t = f.readlines()
reader_dict = csv.DictReader(t)
columns_dict = {k:v for k,v in zip(columns, reader_dict.fieldnames)}

# We'll check for duplicates at the end and prompt the user.
# Since we need to loop over the CSV twice, store it into a dict `d`
d = [row for row in reader_dict]

# Create the headers and empty array to store dhcp_report info
report_columns = columns + [
    'ip',
    'os_xfer_msg', 'os_xfer_time',
    'config_xfer_msg', 'config_xfer_time',
    'msg'
    ]
report_d = [] #empty array to store dhcp_report dictionary rows

# Do all the magic to the dhcpd file from the CSV information
msg = '[INFO] Creating new dhcpd.conf file from csv.'
print(msg)
syslog(msg)
for n,row in enumerate(d, start=1):
    report_d.append(dict.fromkeys(report_columns))
    reportrow = report_d[-1]
    report_msg = ''
    while True:
        if any((
            gateway == ip_addr, 
            file_server == ip_addr, 
            mgmt_ip_addr == ip_addr
            )):
            ip_addr += 1
            msg = f"[Warning] IP `{ip_addr}` conflicts with the server, \
gateway, or mgmt_ip. It is being skipped."
            print(msg)
            syslog(msg)
        else:
            break
    if ip_addr >= dhcp_start:
        msg = f"[Warning] IP range has been exhausted. \
Current IP: `{ip_addr}`. No additional devices will be added."
        print(msg)
        syslog(msg)
        break
    output = client_templates
    # Model / Hardware type 
    hardware = row[columns_dict['hardware']].strip()
    mac = row[columns_dict['mac']].strip()
    os_image = os_file = row[columns_dict['os']].strip()
    config_file = cf_file = row[columns_dict['config']].strip()
    if not any(
            (model := x) for x in device_models
            if x in re.sub('[ :.-]', '', hardware.lower())
            ):
        msg = f"Hardware `{hardware}` not found. Skipping device."
        report_msg += msg
        reportrow.update({
            'hardware': hardware,
            'mac': mac,
            'os': os_image,
            'config': config_file,
            'msg': report_msg,
        })
        msg = f"[Warning] Line {n} of `{csv_filename.name}`: {msg}"
        print(msg)
        syslog(msg)
        continue
    # Create a hostname based on the model type and a unique number
    hostname = f'{model}-{n:03d}'
    # MAC ADDR
    if not mac:
        reportrow.update({
            'hardware': hardware,
            'mac': mac,
            'os': os_image,
            'config': config_file,
            'msg': report_msg,
        })
        continue
    if not mactools.is_mac(mac):
        msg = 'MAC not valid. Skipping device.'
        report_msg += msg
        reportrow.update({
            'hardware': hardware,
            'mac': mac,
            'os': os_image,
            'config': config_file,
            'msg': report_msg,
        })
        msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
        print(msg)
        syslog(msg)
        continue
    if device_models[model]['incr_mac']:
        macaddr = mactools.incr_mac(mac, device_models[model]['incr_mac'])
    else:
        macaddr = mactools.std_mac_format(mac)
    # OS image
    ftp_os_path = ftpd_root_native_path / ftp_os_image_virtual_path
    tftp_os_path = tftpd_root_native_path / tftp_os_image_virtual_path
    if os_image:
        # Test if the file exists, but expect the user to forget the
        # file ext and guess it for them. Select first match only.
        ftp_os_files = sorted((ftp_os_path).glob(f'{os_image}.*'))
        tftp_os_files = sorted((tftp_os_path).glob(f'{os_image}.*'))
        if (ftp_os_path / os_image).exists():
            os_file = (ftp_os_path / os_image).name
        elif (tftp_os_path / os_image).exists():
            os_file = (ftp_os_path / os_image).name
        elif ftp_os_files:
            os_file = min(ftp_os_files, key=lambda x: x.name).name
            msg = f'OS file `{os_image}` was not found, but a similar \
file `{os_file}` was. Adding that file to dhcpd instead.'
            report_msg += msg
            msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
            print(msg)
            syslog(msg)
        elif tftp_os_files:
            os_file = min(tftp_os_files, key=lambda x: x.name).name
            msg = f'OS file `{os_image}` was not found, but a similar \
file `{os_file}` was. Adding that file to dhcpd instead.'
            report_msg += msg
            msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
            print(msg)
            syslog(msg)
        else:
            os_file = ''
    ftp_os_image = '/' / ftp_os_image_virtual_path / os_file
    tftp_os_image = '/' / tftp_os_image_virtual_path / os_file
    # Config file
    ftp_cf_path = ftpd_root_native_path / ftp_config_file_virtual_path
    tftp_cf_path = tftpd_root_native_path / tftp_config_file_virtual_path
    if config_file:
        # Test if the file exists, but expect the user to forget the
        # file ext and guess it for them. Select first match only.
        ftp_conf_files = sorted((ftp_cf_path).glob(f'{config_file}.*'))
        tftp_conf_files = sorted((tftp_cf_path).glob(f'{config_file}.*'))
        if (ftp_cf_path / config_file).exists():
            cf_file = (ftp_cf_path / config_file).name
        elif (tftp_cf_path / config_file).exists():
            cf_file = (tftp_cf_path / config_file).name
        elif ftp_conf_files:
            cf_file = min(ftp_conf_files, key=lambda x: x.name).name
            msg = f'Config file `{config_file}` was not found, but a \
similar file `{cf_file}` was. Adding that file to dhcpd instead.'
            report_msg += msg
            msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
            print(msg)
            syslog(msg)
        elif tftp_conf_files:
            cf_file = min(tftp_conf_files, key=lambda x: x.name).name
            msg = f'Config file `{config_file}` was not found, but a \
similar file `{cf_file}` was. Adding that file to dhcpd instead.'
            report_msg += msg
            msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
            print(msg)
            syslog(msg)
        else:
            cf_file = ''
    ftp_config_file = '/' / ftp_config_file_virtual_path / cf_file
    tftp_config_file = '/' / tftp_config_file_virtual_path / cf_file
    # Can't do anything without either an OS or a config file
    if not os_file and not cf_file:
        msg = f'OS file `{os_image}` nor config file `{config_file}` were \
found in ftp/tftp folder. Skipping device.'
        report_msg += msg
        reportrow.update({
            'hardware': hardware,
            'mac': mac,
            'os': os_image,
            'config': config_file,
            'msg': report_msg,
        })
        msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
        print(msg)
        syslog(msg)
        continue
    if not os_file:
        msg = f'OS file `{os_image}` was not found in ftp/tftp folder. \
Skipping OS image.'
        report_msg += msg
        reportrow.update({
            'os_xfer_msg': 'No file',
        })
        msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
        print(msg)
        syslog(msg)
        output = {
                key:re.sub('.*os_image.*\n', '', template)
                for key, template in output.items()
                }
    if not cf_file:
        msg = f'Config file `{config_file}` was not found in tp/tftp \
folder. Skipping config file.'
        report_msg += msg
        reportrow.update({
            'config_xfer_msg': 'No file',
        })
        msg = f'[Warning] Line {n} of `{csv_filename.name}`: Hardware \
`{hardware}`, MAC `{mac}`. {msg}'
        print(msg)
        syslog(msg)
        output = {
                key:re.sub('.*config_file.*\n', '', template)
                for key, template in output.items()
                }
    output = output[device_models[model]['vendor']].format_map(vars())
    with open(dhcpd_tmp_config_file, mode='a') as f:
        f.write(output)
    reportrow.update({
        'hardware': hardware,
        'mac': mac,
        'os': os_image,
        'config': config_file,
        'ip': ip_addr,
        'msg': report_msg,
    })
    ip_addr += 1

# Now we search and notify the user of duplicates
m = tuple(row[columns_dict['mac']] for row in d)
c = tuple(row[columns_dict['config']] for row in d)

# Search for duplicate configs
unique_configs = set()
dup_pos_configs = []
for n, v in enumerate(c):
    if v == '':
        continue
    if not v in unique_configs:
        unique_configs.add(v)
    else:
        dup_pos_configs.append(n)
if dup_pos_configs:
    msg = '[NOTICE] ***Duplicate config files found!***'
    print(msg)
    syslog(msg)
for n in dup_pos_configs:
    msg = f"[NOTICE] Line {n+1} of `{csv_filename.name}`: \
Duplicate config file. {d[n][columns_dict['config']]}"
    print(msg)
    syslog(msg)

# Search for duplicate MACs
unique_macs = set()
dup_pos_macs = []
for n, v in enumerate(m):
    if v == '':
        continue
    if not v in unique_macs:
        unique_macs.add(v)
    else:
        dup_pos_macs.append(n)
if dup_pos_macs:
    msg = '[NOTICE] ***Duplicate MACs found!***'
    print(msg)
    syslog(msg)
for n in dup_pos_macs:
    msg = f"[NOTICE] Line {n+1} of `{csv_filename.name}`: \
Duplicate MAC. {d[n][columns_dict['mac']]}"
    print(msg)
    syslog(msg)

# Set IP after static hosts as the start of the dynamic range 
# unless the range is already exhausted
if ip_addr >= dhcp_start:
    ip_addr = dhcp_start
else:
    dhcp_start = ip_addr
    output = re.sub(
        r'(range )(([0-9]{1,3}\.?){4})', 
        f'\g<1>{dhcp_start}', 
        dhcpd_tmp_config_file.read_text()
        )
    dhcpd_tmp_config_file.write_text(output)

# Copy working templates to the server daemon locations
print(f'Copying `{dhcpd_tmp_config_file}` to `{dhcpd_config_file_loc}`')
dhcpd_config_file_loc.write_text(dhcpd_tmp_config_file.read_text())

# Write the dhcp_report.csv file
def dhcp_report_write(d, columns=report_columns):
    with open(dhcp_report, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(d)
dhcp_report_write(report_d, report_columns)

# Done. Ready to go
msg = '[INFO] Finished reconfiguring files. Ready!'
print(msg)
syslog(msg)
