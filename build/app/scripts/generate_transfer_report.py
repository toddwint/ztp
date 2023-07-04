#!/usr/bin/env python3
"""
Use the information in the logs to update `transfer_report.csv` with times
of successful file transfers.
"""

__version__ = '0.0.2'
__author__ = 'Todd Wintermute'
__date__ = '2023-06-29'

import csv
import datetime as dt
import ipaddress
import json
import os
import pathlib
import re
import subprocess
import sys

appname = os.environ['APPNAME']
hostname = os.environ['HOSTNAME']
dhcp_report = pathlib.Path(f"/opt/{appname}/logs/dhcp_report.csv")
xfer_report = pathlib.Path(f"/opt/{appname}/ftp/transfer_report.csv")
vendor_csv_file = pathlib.Path(
    f"/opt/{appname}/ftp/vendor_class_defaults.csv"
    )
report_csv_columns = [
    'hardware', 'mac', 'os', 'config', 'ip',
    'os_xfer_msg', 'os_xfer_time', 'config_xfer_msg', 'config_xfer_time', 
    'msg'
    ]
vendor_csv_columns = ['hardware','vendor_cid','os','config']
ztp_csv_file = pathlib.Path(f"/opt/{appname}/ftp/ztp.csv")
dhcpd_config_file_loc = pathlib.Path('/etc/dhcp/dhcpd.conf')
ztp_log = pathlib.Path(f"/opt/{appname}/logs/ztp.log")
ftp_log = pathlib.Path(f"/opt/{appname}/logs/vsftpd_xfers.log")
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
now = dt.datetime.now()
time = now.isoformat(timespec='seconds', sep=' ')
ts = str(now).split('.')[0].translate({45: '', 32: '', 58: '', 46: ''})

if not all((dhcp_report.exists(), ztp_log.exists())):
    print(f"Error accessing `{dhcp_report}` or `{ztp_log}` file. Bye.")
    sys.exit()

# tftp regexes
os_process_search = '.*\[(?P<process>\d+)\].*{ip}.*{os}.*'
config_process_search = '.*\[(?P<process>\d+)\].*{ip}.*{config}.*'
process_line = '.*\[{process}\].*'
os_search = (
    '(?P<time>.*) 'f'{hostname}' '.*\[(?P<process>{process})\]: (?P<msg>.*)'
    )
config_search = (
    '(?P<time>.*) 'f'{hostname}' '.*\[(?P<process>{process})\]: (?P<msg>.*)'
    )
xfer_error_msgs = [
    'fail download', 'sending nak', 'connection refused', 'incomplete'
    ]
xfer_msgs = ['ok download', 'complete']
xfer_error_msgs = f"({'|'.join(xfer_error_msgs)})"
xfer_msgs = f"({'|'.join(xfer_msgs)})"
xfer_error = re.compile(f'({xfer_error_msgs})', re.IGNORECASE)
xfer_msg = re.compile(f'(xfer_msgs)', re.IGNORECASE)
file_xfer_search = (
    '.*(?P<ip>{ip}).*/(?P<type>config|os)(?:_files|_images)/(?P<file>{file})'
    )
# ftp regexes
ftp_os_search = (
    '(?P<time>.*) \d+ .*(?P<ip>{ip}).*(?P<os>{os}).* (?P<status>\w.*)'
    )
ftp_config_search = (
    '(?P<time>.*) \d+ .*(?P<ip>{ip}).*(?P<config>{config}).* (?P<status>\w.*)'
    )
ftp_xfer_search = (
    '(?P<time>.*)\s+\d+\s+.*(?P<ip>{ip}).*/(?:config_files|os_images)'
    '/(?P<file>[^\s]+).*\s+(?P<status>\w+).*'
    )

# dhcp lease regexes
dhcp_lease_search = (
    '(?P<mac>[0-9a-fA-F:]+)\s+(?P<ip>[0-9.]+)\s+(?P<hostname>[^\s]+)\s+.*'
    )

# dhcpd starting and ending ip search
dhcp_range_search = 'range\s+(?P<ip_start>[0-9.]+)\s+(?P<ip_end>[0-9.]+)'

def ftp_os_xfer_search(row):
    ftp_log_reverse = '\n'.join(ftp_log_text.splitlines()[::-1])
    ftp_os_match = re.search(
        ftp_os_search.format_map(row), 
        ftp_log_reverse
        )
    if ftp_os_match:
        if ftp_os_match['status'] == 'c':
            row['os_xfer_msg'] = 'Complete'
            row['os_xfer_time'] = ftp_os_match['time']
        elif ftp_os_match['status'] == 'i':
            row['os_xfer_msg'] = 'Incomplete'
            row['os_xfer_time'] = ftp_os_match['time']
        else:
            row['os_xfer_msg'] = 'Unknown Error'
            row['os_xfer_time'] = time
    return row

def ftp_config_xfer_search(row):
    ftp_log_reverse = '\n'.join(ftp_log_text.splitlines()[::-1])
    ftp_config_match = re.search(
        ftp_config_search.format_map(row), 
        ftp_log_reverse
        )
    if ftp_config_match:
        if ftp_config_match['status'] == 'c':
            row['config_xfer_msg'] = 'Complete'
            row['config_xfer_time'] = ftp_config_match['time']
        elif ftp_config_match['status'] == 'i':
            row['config_xfer_msg'] = 'Incomplete'
            row['config_xfer_time'] = ftp_config_match['time']
        else:
            row['config_xfer_msg'] = 'Unknown Error'
            row['config_xfer_time'] = time
    return row

def tftp_os_xfer_search(row):
    search = os_process_search.format_map(row)
    os_processes = re.findall(search, log_text)
    if os_processes:
        # found atleast one process with os file xfer
        tmp_row = row | {'process': os_processes[-1]}
        lines = re.findall(process_line.format_map(tmp_row), log_text)
        xfer_errors = [xfer_error.search(line) for line in lines]
        text = '\n'.join(lines[::-1])
        os_match = re.search(os_search.format_map(tmp_row), text)
        if not any(xfer_errors):
            # then it transfered ok, I guess
            row['os_xfer_msg'] = 'Read request'
            row['os_xfer_time'] = os_match['time']
        elif any(xfer_errors):
            row['os_xfer_msg'] = 'Error'
            row['msg'] += os_match['msg'] + '. '
            row['os_xfer_time'] = os_match['time']
        else:
            row['os_xfer_msg'] = f'Unknown Error'
            row['os_xfer_time'] = time
    return row

def tftp_config_xfer_search(row):
    search = config_process_search.format_map(row)
    config_processes = re.findall(search, log_text)
    if config_processes:
        # found atleast one process with config file xfer
        tmp_row = row | {'process': config_processes[-1]}
        lines = re.findall(process_line.format_map(tmp_row), log_text)
        xfer_errors = [xfer_error.search(line) for line in lines]
        text = '\n'.join(lines[::-1])
        config_match = re.search(config_search.format_map(tmp_row), text)
        if not any(xfer_errors):
            # then it transfered ok, I guess
            row['config_xfer_msg'] = 'Read request'
            row['config_xfer_time'] = config_match['time']
        elif any(xfer_errors):
            row['config_xfer_msg'] = 'Error'
            row['msg'] += config_match['msg'] + '. '
            row['config_xfer_time'] = config_match['time']
        else:
            row['config_xfer_msg'] = f'Unknown Error'
            row['config_xfer_time'] = time
    return row

def get_dhcp_lease_list():
    current_dhcp_leases = subprocess.run(
        'dhcp-lease-list', capture_output=True, universal_newlines=True
        )
    dhcp_leases = [
        m.groupdict() for line in current_dhcp_leases.stdout.splitlines() 
        if (m := re.search(dhcp_lease_search, line))
            ]
    return dhcp_leases

def add_new_leases(dhcp_objs, dhcp_leases):
    # Append unknown DHCP leases to dhcp_objs
    noseps = {58: '', 45: '', 32: ''}
    # Add new clients to dhcp_report variable, save them later
    if dhcp_leases:
        new_leases = [
            {'mac': client['mac'], 'ip': client['ip']} 
            for client in dhcp_leases 
                if client['mac'].translate(noseps).lower() not in 
                [x['mac'].translate(noseps).lower() for x in dhcp_objs 
                    if x['mac']]
                ]
        for each in new_leases:
            tmp_dict = dict.fromkeys(report_csv_columns)
            tmp_dict.update(each)
            dhcp_objs.append(tmp_dict)
    return dhcp_objs

def add_files_for_new_leases(dhcp_objs, dhcp_leases):
    # First determine if this dhcp_lease is not in the static range
    dhcpd_text = dhcpd_config_file_loc.read_text()
    dhcp_range_match = re.search(dhcp_range_search, dhcpd_text)
    ip_start = ipaddress.ip_address(dhcp_range_match['ip_start'])
    ip_end = ipaddress.ip_address(dhcp_range_match['ip_end'])
    # Now try to fill in the hardware, os, and config from the unknown DHCPs
    for row in dhcp_objs:
        if not (row['ip'] and ipaddress.ip_address(row['ip']) >= ip_start):
            continue
        re_dict = row | {'file': '|'.join(re_vendor_files)}
        filematches = [ 
            m for line in log_text.splitlines()
            if (m := re.search(file_xfer_search.format_map(re_dict), line))
                ]
        for filematch in filematches:
            if not row['config'] and filematch['type'] == 'config':
                row['config'] = filematch['file']
                row['hardware'] = hardware_lut[filematch['file']]
            elif not row['os'] and filematch['type'] == 'os':
                    row['os'] = filematch['file']
                    row['hardware'] = hardware_lut[filematch['file']]
    # Save unknown DHCP info back to dhcp_report
    with open(dhcp_report, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=report_csv_columns)
        writer.writeheader()
        writer.writerows(dhcp_objs)
    return dhcp_objs

log_text = ztp_log.read_text()
ftp_log_text = ftp_log.read_text()

# Read the vendor_class_defaults CSV
if not vendor_csv_file.exists():
    msg = f'[INFO] `{vendor_csv_file.name}` was not found.'
    print(msg)
    vendor_objs = [] # we still need the program to run
else:
    with open(vendor_csv_file) as f:
        t = f.readlines()
    reader_dict = csv.DictReader(t, fieldnames=vendor_csv_columns)
    original_vendor_columns = reader_dict.__next__() # remove original header
    # List of the data objects
    vendor_objs = [row for row in reader_dict]
    # Hardware look up table
    hardware_lut =  {
        each['config']: each['hardware'] 
        for each in vendor_objs if each['config']
            } | {
        each['os']: each['hardware'] 
        for each in vendor_objs if each['os']
            }
    # List of all the entered filenames in vendor CSV
    vendor_files = [
        os for each in vendor_objs 
        if (os := each['os'])
        ] + [
        config for each in vendor_objs 
        if (config := each['config'])
        ]
    # List of filenames save for use in a regex
    re_vendor_files = [re.escape(each) for each in vendor_files]

# Read the ZTP CSV (only to display a message on the transfer report)
if not ztp_csv_file.exists():
    msg = f'[INFO] `{ztp_csv_file.name}` was not found.'
    print(msg)

# Read the dhcp_report CSV
with open(dhcp_report) as f:
    t = f.readlines()
reader_dict = csv.DictReader(t, fieldnames=report_csv_columns)
original_report_columns = reader_dict.__next__() # remove original header
dhcp_objs = [row for row in reader_dict]
dhcp_leases = get_dhcp_lease_list()
# Add any unknown dhcp requests using vendor class specific entries
dhcp_objs = add_new_leases(dhcp_objs, dhcp_leases)
if vendor_csv_file.exists():
    dhcp_objs = add_files_for_new_leases(dhcp_objs, dhcp_leases)

# Look for transfers and update transfer columns
for row in dhcp_objs:
    if not row['ip']:
        # No DHCP IP so nothing to search for
        continue
    if row['os']: # run if the OS was specified in the dhcp_config
        if device_models[row['hardware']]['vendor'].lower() == 'juniper':
            row = ftp_os_xfer_search(row)
        else:
            row = tftp_os_xfer_search(row)
    if row['config']: # run if the config was specified in the dhcp_config
        if device_models[row['hardware']]['vendor'].lower() == 'juniper':
            row = ftp_config_xfer_search(row)
        else:
            row = tftp_config_xfer_search(row)

with open(xfer_report, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=report_csv_columns)
    writer.writeheader()
    writer.writerows(dhcp_objs)

rval = subprocess.run(f"chown $HUID:$HGID {str(xfer_report)}", shell=True)
