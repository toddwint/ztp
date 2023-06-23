#!/usr/bin/env python3
"""
Use the information in the logs to update `transfer_report.csv` with times
of successful file transfers.
"""

# Pseudo code
#   Iterate over IPs in dhcp_config.csv
#   If dhcp_config.csv has os, search for all matching xfers
#   If dhcp_config.csv has config, search for all matching xfers
#   Reduce matches to the latest processes or reverse order
#   Eliminate any failed transfers
#   Prefer to search the vsftpd log file before the syslog

__version__ = '0.0.1'
__author__ = 'Todd Wintermute'
__date__ = '2023-06-22'

import csv
import datetime as dt
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
ztp_log = pathlib.Path(f"/opt/{appname}/logs/ztp.log")
ftp_log = pathlib.Path(f"/opt/{appname}/logs/vsftpd_xfers.log")
device_models_json = f'/opt/{appname}/scripts/device_models.json'
device_models_json = pathlib.Path(device_models_json)
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
os_search = \
'(?P<time>.*) 'f'{hostname}' '.*\[(?P<process>{process})\]: (?P<msg>.*)'
config_search = \
'(?P<time>.*) 'f'{hostname}' '.*\[(?P<process>{process})\]: (?P<msg>.*)'
xfer_error_msgs = [
    'fail download', 'sending nak', 'connection refused', 'incomplete'
    ]
xfer_msgs = ['ok download', 'complete']
xfer_error_msgs = f"({'|'.join(xfer_error_msgs)})"
xfer_msgs = f"({'|'.join(xfer_msgs)})"
xfer_error = re.compile(f'({xfer_error_msgs})', re.IGNORECASE)
xfer_msg = re.compile(f'(xfer_msgs)', re.IGNORECASE)

# ftp regexes
ftp_os_search = \
'(?P<time>.*) \d+ .*(?P<ip>{ip}).*(?P<os>{os}).* (?P<status>\w.*)'
ftp_config_search = \
'(?P<time>.*) \d+ .*(?P<ip>{ip}).*(?P<config>{config}).* (?P<status>\w.*)'

log_text = ztp_log.read_text()
ftp_log_text = ftp_log.read_text()

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

columns = [
    'hardware', 'mac', 'os', 'config', 'ip',
    'os_xfer_msg', 'os_xfer_time', 'config_xfer_msg', 'config_xfer_time', 
    'msg'
    ]

with open(dhcp_report) as f:
    t = f.readlines()
reader_dict = csv.DictReader(t)
columns_dict = {k:v for k,v in zip(columns, reader_dict.fieldnames)}
d = [row for row in reader_dict]

for row in d:
    if not row['ip']:
        # No DHCP IP so nothing to search for
        continue
    if row['os']: # run if the OS was specified in the dhcp_config
        if device_models[row['hardware']]['protocol'] == 'ftp':
            row = ftp_os_xfer_search(row)
        else:
            row = tftp_os_xfer_search(row)
    if row['config']: # run if the config was specified in the dhcp_config
        if device_models[row['hardware']]['protocol'] == 'ftp':
            row = ftp_config_xfer_search(row)
        else:
            row = tftp_config_xfer_search(row)

with open(xfer_report, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=columns_dict.values())
    writer.writeheader()
    writer.writerows(d)

rval = subprocess.run(f"chown $HUID:$HGID {str(xfer_report)}", shell=True)
