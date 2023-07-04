#!/usr/bin/env python3
"""
 Input a ztp.csv that has the Hardware,MAC,OS,Config and output a modified 
 dhcpd.conf file based on a template.
 Optionally, input a vendor class defaults CSV file with the fields
 Hardware,Vendor Class ID, OS, Config and modify the dhcpd.conf file.
 Also, generate a dhcp_report.csv file to be used later to monitor
 the progress of the file transfers.
 Script will replace the dhcpd, tftp, and ftp configuration files,
 and then restart the processes.
"""
__version__ = '0.0.9'
__date__ = '2023-07-04'
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
starting_ip = '192.168.10.1'
file_server = '192.168.1.252'
mgmt_ip = '192.168.1.253'
gateway = '192.168.1.254'
dhcp_start = '192.168.1.249'
dhcp_end = '192.168.1.250'
ztp_csv_file = pathlib.Path('ztp.csv')
ztp_csv_path = pathlib.Path(f'/opt/{appname}/ftp')
vendor_csv_file = pathlib.Path('vendor_class_defaults.csv')
vendor_csv_path = pathlib.Path(f'/opt/{appname}/ftp')
dhcp_report_template = pathlib.Path(
    f'/opt/{appname}/configs/dhcp_report.csv.template'
    )
dhcp_report = pathlib.Path(f'/opt/{appname}/logs/dhcp_report.csv')
dhcpd_daemon_name = 'isc-dhcp-server'
dhcpd_template = pathlib.Path(f'/opt/{appname}/configs/dhcpd.conf')
dhcpd_tmp_config_file = pathlib.Path(f'/opt/{appname}/configs/dhcpd.py.conf')
dhcpd_config_file_loc = pathlib.Path('/etc/dhcp/dhcpd.conf')
root = pathlib.Path('/')
ftp_explicit_path = pathlib.Path(f'/opt/{appname}/ftp')
os_folder = 'os_images'
config_folder = 'config_files'
vendor_csv_columns = ['hardware','vendor_cid','os','config']
ztp_csv_columns = ['hardware', 'mac', 'os', 'config']
report_columns = ztp_csv_columns + [
    'ip',
    'os_xfer_msg', 'os_xfer_time',
    'config_xfer_msg', 'config_xfer_time',
    'msg'
    ]

device_models_json = pathlib.Path(
    f'/opt/{appname}/ftp/supported_device_models.json'
    )
try:
    device_models = json.loads(device_models_json.read_text())
except:
    device_models_json = pathlib.Path(
        f'/opt/{appname}/configs/supported_device_models.json'
        )
    device_models = json.loads(device_models_json.read_text())
vendor_class = """\
#Class to Match Option 60
class "Vendor-Class" {
        match option vendor-class-identifier;
}\
"""

vendor_subclasses = {
    'juniper': """\
    subclass "Vendor-Class" "{vendor_cid}" {{
        option ztp.juniper-transfer-mode ftp;
        option ztp.juniper-ftp-timeout "3600";
        option ztp.juniper-image-file-name "{os}";
        option ztp.juniper-config-file-name "{config}";
        }}\
""",
    'aruba': """\
    subclass "Vendor-Class" "{vendor_cid}" {{
        option ztp.aruba-image-file-name "{os}";
        option ztp.aruba-config-file-name "{config}";
        }}\
""",
}

client_templates = {
        'juniper': """
host {hostname} {{
    hardware ethernet {mac};
    fixed-address {ip};
    option ztp.juniper-transfer-mode ftp;
    option ztp.juniper-ftp-timeout "3600";
    option ztp.juniper-image-file-name "{os}";
    option ztp.juniper-config-file-name "{config}";
}}\
""",
        'aruba': """
host {hostname} {{
    hardware ethernet {mac};
    fixed-address {ip};
    option ztp.aruba-image-file-name "{os}";
    option ztp.aruba-config-file-name "{config}";
}}\
"""
}

# Create command line arguments (optionally to get a different filename)
parser = argparse.ArgumentParser(
    description='Generate dhcpd.conf file from CSV file.',
    epilog='Have a great day!',
    )
parser.add_argument(
    '-v', '--version',
    help='show the version number and exit',
    action='version',
    version=f'Version: {__version__}',
    )
parser.add_argument(
    'ztp_csv',
    nargs='?',
    type=pathlib.Path,
    default=ztp_csv_file,
    help=f'name of ZTP CSV file (default={ztp_csv_file})',
    )
parser.add_argument(
    '-i', '--vendor_csv',
    nargs='?',
    type=pathlib.Path,
    default=vendor_csv_file,
    help=f'name of Vendor Class CSV file (default={vendor_csv_file})',
    )
args = parser.parse_args()

if ztp_csv_file == args.ztp_csv:
    ztp_csv_file = ztp_csv_path / args.ztp_csv
else:
    ztp_csv_file = args.ztp_csv
if vendor_csv_file == pathlib.Path(args.vendor_csv):
    vendor_csv_file = vendor_csv_path / args.vendor_csv
else:
    vendor_csv_file = pathlib.Path(args.vendor_csv)

ip = ipaddress.IPv4Address(starting_ip)
mgmt_ip = ipaddress.IPv4Address(mgmt_ip)
file_server = ipaddress.IPv4Address(file_server)
gateway = ipaddress.IPv4Address(gateway)
dhcp_start = ipaddress.IPv4Address(dhcp_start)
dhcp_end = ipaddress.IPv4Address(dhcp_end)

# Make working copies of template files which will be modified
print(f'Making `{dhcpd_tmp_config_file}` from `{dhcpd_template}`')
dhcpd_tmp_config_file.write_text(dhcpd_template.read_text())
print(f'Making `{dhcp_report}` from `{dhcp_report_template}`')
dhcp_report.write_text(dhcp_report_template.read_text())

# Start of Vendor Class ID section
if not vendor_csv_file.exists():
    msg = f'[WARNING] `{vendor_csv_file.name}` was not found. '
    print(msg)
    syslog(msg)
    vendor_objs = [] # we still need the program to run
else:
    with open(vendor_csv_file) as f:
        t = f.readlines()
    reader_dict = csv.DictReader(t, fieldnames=vendor_csv_columns)
    original_vendor_columns = reader_dict.__next__() # remove original header
    # List of the data objects
    vendor_objs = [row for row in reader_dict]

tmp_vendor_objs = [] # new list to store valid data objects
for n,item in enumerate(vendor_objs, 1):
    tmp_vendor_objs.append(item.copy())
    index = tmp_vendor_objs.index(item)
    tmp_item = tmp_vendor_objs[index]
    hardware = item['hardware'].strip()
    vendor_cid = item['vendor_cid'].strip()
    os = item['os'].strip()
    config = item['config'].strip()
    # os and config are the original file names from Vendor ClassID CSV file
    # os_file and cf_file are the actual files with ext, if forgotten
    sysloghdr = (
        f'[WARNING] Line {n} of `{vendor_csv_file.name}`: '
        f'Hardware `{hardware}`. '
        )
    if hardware not in device_models.keys():
        msg = 'Hardware not valid. Skipping device. '
        print(msg)
        syslog(sysloghdr + msg)
        tmp_vendor_objs.remove(tmp_item)
        continue
    vendor = device_models[hardware]['vendor']
    tmp_item['template'] = vendor_subclasses[vendor]
    if not vendor_cid:
        msg = 'Vendor class id missing. Skipping device. '
        print(msg)
        syslog(sysloghdr + msg)
        tmp_vendor_objs.remove(tmp_item)
        continue
    number_of_matches = [
        each['vendor_cid'] == item['vendor_cid'] 
        for each in tmp_vendor_objs
        ].count(True)
    sysloghdr = (
        f'[WARNING] Line {n} of `{vendor_csv_file.name}`: '
        f'Hardware `{hardware}`, Vendor ID `{vendor_cid}`. '
        )
    if number_of_matches > 1:
        msg = 'Vendor string already exists. Skipping device. '
        print(msg)
        syslog(sysloghdr + msg)
        tmp_vendor_objs.remove(tmp_item)
        continue
    os_path = ftp_explicit_path / os_folder
    os_file = os_path / os
    os_files = sorted((os_path).glob(f'{os}.*'))
    if os and os_file.exists():
        tmp_item['os'] = root / os_folder / os
    elif os and os_files:
        os_file = min(os_files, key=lambda x: x.name).name
        tmp_item['os'] = root / os_folder / os_file
        msg = (
            f'OS file was not found, but a similar file `{os_file}` was. '
            'Adding that file to dhcpd.conf instead. '
            )
        print(msg)
        syslog(sysloghdr + msg)
    else:
        if os:
            msg = (
                f'OS file was not found in ftp folder. '
                'Skipping OS image. '
                )
            print(msg)
            syslog(sysloghdr + msg)
        tmp_item['os'] = ''
        tmp_item['template'] = re.sub(
            '.*\{os\}.*\n',
            '', 
            tmp_item['template']
            )
    cf_path = ftp_explicit_path / config_folder
    cf_file = cf_path / config
    cf_files = sorted((cf_path).glob(f'{config}.*'))
    if config and cf_file.exists():
        tmp_item['config'] = root / config_folder / config
    elif config and cf_files:
        cf_file = min(cf_files, key=lambda x: x.name).name
        tmp_item['config'] = root / config_folder / cf_file
        msg = (
            f'Configuration file was not found, but a similar file '
            f'`{cf_file}` was. Adding that file to dhcpd.conf instead. '
            )
        print(msg)
        syslog(sysloghdr + msg)
    else:
        if config:
            msg = (
                f'Configuration file was not found in ftp folder. '
                'Skipping configuration file. '
                )
            print(msg)
            syslog(sysloghdr + msg)
        tmp_item['config'] = ''
        tmp_item['template'] = re.sub(
            '.*\{config\}.*\n',
            '',
            tmp_item['template']
            )
    if not any((tmp_item['os'], tmp_item['config'])):
        if any((os, config)):
            msg = (
                'OS file nor configuration file were found in ftp folder. '
                'Skipping device. '
                )
            print(msg)
            syslog(sysloghdr + msg)
        else:
            msg = (
                f'No OS file nor configuration file were specified. '
                'Skipping device. '
                )
            # Below is commented as it is understood nothing will happend
            #print(msg)
            #syslog(sysloghdr + msg)
        tmp_vendor_objs.remove(tmp_item)
        continue
    tmp_item['template'] = tmp_item['template'].format_map(tmp_item)
if tmp_vendor_objs:
    msg = '[INFO] Adding Vendor Class ID info to dhcpd.conf '
    print(msg)
    syslog(msg)
else:
    msg = '[INFO] Vendor Class ID info will not be added to dhcpd.conf '
    print(msg)
    syslog(msg)

dhcpd_text = dhcpd_tmp_config_file.read_text()
dhcpd_sections = dhcpd_text.split('\n\n')
add_lines = [each['template'] for each in tmp_vendor_objs]
add_text = '\n'.join(add_lines) + '\n}\n'
if tmp_vendor_objs:
    dhcpd_sections.insert(2, vendor_class)
    ztp_section = dhcpd_sections.pop(4)
    endbrkt = ztp_section.index('}')
    ztp_section = ztp_section[:endbrkt] + add_text
    dhcpd_sections.insert(4, ztp_section)
    dhcpd_tmp_config_file.write_text('\n\n'.join(dhcpd_sections))
# End of Vendor Class ID section

# Start of MAC ADDR method ztp.csv section
if not ztp_csv_file.exists():
    msg = f'[WARNING] `{ztp_csv_file.name}` was not found. '
    print(msg)
    syslog(msg)
    ztp_objs = [] # we still need the program to run
else:
    # Read the CSV file, store it, get the headers, and close the file 
    with open(ztp_csv_file) as f:
        t = f.readlines()
    reader_dict = csv.DictReader(t, fieldnames=ztp_csv_columns)
    original_ztp_columns = reader_dict.__next__() # remove original header
    # List of the data objects
    ztp_objs = [row for row in reader_dict]

# Do all the magic to the dhcpd file from the ZTP CSV information
report_ztp = [] #empty array to store dhcp_report data objs
tmp_ztp_objs = [] # new list to store valid data objects
for n,item in enumerate(ztp_objs, start=1):
    while True:
        if any((
            gateway == ip, 
            file_server == ip, 
            mgmt_ip == ip
            )):
            ip += 1
            msg = (
                f'[Warning] IP `{ip}` conflicts with the server, gateway, '
                'or mgmt ip. It is being skipped. '
                )
            print(msg)
            syslog(msg)
        else:
            break
    if ip >= dhcp_start:
        msg = (
            f'[Warning] IP range has been exhausted. Current IP: `{ip}`. '
            'No additional devices will be added. '
            )
        print(msg)
        syslog(msg)
        break
    report_ztp.append(dict.fromkeys(report_columns))
    reportrow = report_ztp[-1]
    report_msg = ''
    tmp_ztp_objs.append(item.copy())
    index = tmp_ztp_objs.index(item)
    tmp_item = tmp_ztp_objs[index]
    hardware = item['hardware'].strip()
    mac = item['mac'].strip()
    os = item['os'].strip()
    config = item['config'].strip()
    # os and config are the original file names from ZTP CSV file
    # os_file and cf_file are the actual files with ext, if forgotten
    sysloghdr= f'[Warning] Line {n} of `{ztp_csv_file.name}`: '
    if not any(
            (model := x) for x in device_models
            if x in re.sub('[ :.-]', '', hardware.lower())
            ):
        msg = f'Hardware `{hardware}` not found. Skipping device. '
        report_msg += msg
        reportrow.update(item|{'msg': report_msg})
        print(msg)
        syslog(sysloghdr + msg)
        tmp_ztp_objs.remove(tmp_item)
        continue
    vendor = device_models[model]['vendor']
    tmp_item['template'] = client_templates[vendor]
    tmp_item['ip'] = ip
    # Create a hostname based on the model type and a unique number
    tmp_item['hostname'] = f'{model}-{n:03d}'
    # MAC ADDR
    if not mac:
        reportrow.update(item|{'msg': report_msg})
        tmp_ztp_objs.remove(tmp_item)
        continue
    sysloghdr = (
        f'[Warning] Line {n} of `{ztp_csv_file.name}`: '
        f'Hardware `{hardware}`, MAC `{mac}`. '
        )
    if not mactools.is_mac(mac):
        msg = 'MAC not valid. Skipping device. '
        report_msg += msg
        reportrow.update(item|{'msg': report_msg})
        print(msg)
        syslog(sysloghdr + msg)
        tmp_ztp_objs.remove(tmp_item)
        continue
    if device_models[model]['incr_mac']:
        macaddr = mactools.incr_mac(mac, device_models[model]['incr_mac'])
        tmp_item['mac'] = macaddr
    else:
        macaddr = mactools.std_mac_format(mac)
        tmp_item['mac'] = macaddr
    # OS image
    os_path = ftp_explicit_path / os_folder
    os_file = os_path / os
    os_files = sorted((os_path).glob(f'{os}.*'))
    if os and os_file.exists():
        tmp_item['os'] = root / os_folder/ os
    elif os and os_files:
        os_file = min(os_files, key=lambda x: x.name).name
        tmp_item['os'] = root / os_folder/ os_file
        msg = (
            f'OS file was not found, but a similar file `{os_file}` was. '
            'Adding that file to dhcpd.conf instead. '
            )
        report_msg += msg
        reportrow.update(item|{'msg': report_msg})
        print(msg)
        syslog(sysloghdr + msg)
    else:
        if os:
            msg = (
                f'OS file was not found in ftp folder. '
                'Skipping OS image. '
                )
            report_msg += msg
            reportrow.update(item|{'msg': report_msg})
            print(msg)
            syslog(sysloghdr + msg)
        tmp_item['os'] = ''
        tmp_item['template'] = re.sub(
            '.*\{os\}.*\n',
            '', 
            tmp_item['template']
            )
    # Config file
    cf_path = ftp_explicit_path / config_folder
    cf_file = cf_path / config
    cf_files = sorted((cf_path).glob(f'{config}.*'))
    if config and cf_file.exists():
        tmp_item['config'] = root / config_folder / config
    elif config and cf_files:
        cf_file = min(cf_files, key=lambda x: x.name).name
        tmp_item['config'] = root / config_folder / cf_file
        msg = (
            f'Configuration file was not found, but a similar file `{cf_file}` '
            'was. Adding that file to dhcpd.conf instead. '
            )
        report_msg += msg
        reportrow.update(item|{'msg': report_msg})
        print(msg)
        syslog(sysloghdr + msg)
    else:
        if config:
            msg = (
                f'Configuration file was not found in ftp folder. '
                'Skipping configuration file. '
                )
            report_msg += msg
            reportrow.update(item|{'msg': report_msg})
            print(msg)
            syslog(sysloghdr + msg)
        tmp_item['config'] = ''
        tmp_item['template'] = re.sub(
            '.*\{config\}.*\n',
            '',
            tmp_item['template']
            )
    if not any((tmp_item['os'], tmp_item['config'])):
        if any((os,config)):
            msg = (
                f'OS file nor configuration file were found in ftp folder. '
                'Skipping device. '
                )
            report_msg += msg
            reportrow.update(item|{'msg': report_msg})
            print(msg)
            syslog(sysloghdr + msg)
        else:
            reportrow.update(item) 
            msg = (
                f'No OS file nor configuration file were specified. '
                'Skipping device. '
                )
            report_msg += msg
            # Below is commented as it is understood nothing will happend
            #reportrow.update(item|{'msg': report_msg})
            #print(msg)
            #syslog(sysloghdr + msg)
        tmp_ztp_objs.remove(tmp_item)
        continue
    reportrow.update(item|{'ip': ip, 'msg': report_msg})
    ip += 1
    tmp_item['template'] = tmp_item['template'].format_map(tmp_item)
if tmp_ztp_objs:
    msg = '[INFO] Adding MAC ADDR method info from ztp.csv to dhcpd.conf '
    print(msg)
    syslog(msg)
else:
    msg = (
        '[INFO] MAC ADDR method info from ztp.csv will not be added to '
        'dhcpd.conf '
        )
    print(msg)
    syslog(msg)

dhcpd_text = dhcpd_tmp_config_file.read_text()
add_lines = [each['template'] for each in tmp_ztp_objs]
add_text = ''.join(add_lines)
if tmp_ztp_objs:
    add_dhcpd_text = dhcpd_text + add_text
    dhcpd_tmp_config_file.write_text(add_dhcpd_text)
# End of MAC ADDR method ztp.csv section

# Now we search and notify the user of duplicates
m = tuple(item['mac'] for item in ztp_objs)
c = tuple(item['config'] for item in ztp_objs)

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
    msg = '[NOTICE] ***Duplicate configuration files found!*** '
    print(msg)
    syslog(msg)
for n in dup_pos_configs:
    msg = (
        f'[NOTICE] Line {n+1} of `{ztp_csv_file.name}`: '
        f'Duplicate configuration file. {ztp_objs[n]["config"]} '
        )
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
    msg = '[NOTICE] ***Duplicate MACs found!*** '
    print(msg)
    syslog(msg)
for n in dup_pos_macs:
    msg = (
        f'[NOTICE] Line {n+1} of `{ztp_csv_file.name}`: '
        f'Duplicate MAC. {ztp_objs[n]["mac"]} '
        )
    print(msg)
    syslog(msg)

# Set IP after static hosts as the start of the dynamic range 
# unless the range is already exhausted
if ip >= dhcp_start:
    ip = dhcp_start
else:
    dhcp_start = ip
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
def dhcp_report_write(report_objs, columns):
    with open(dhcp_report, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(report_objs)
dhcp_report_write(report_ztp, report_columns)

# Done. Ready to go
msg = '[INFO] Finished reconfiguring files. Ready! '
print(msg)
syslog(msg)
