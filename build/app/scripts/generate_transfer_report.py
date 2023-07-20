#!/usr/bin/env python3
"""
Use information in the syslog to update `transfer_report.csv` with 
file transfer messages.
"""

__version__ = '0.0.3'
__author__ = 'Todd Wintermute'
__date__ = '2023-07-19'

import csv
import datetime as dt
import ipaddress
import json
import os
import pathlib
import re
import subprocess
import sys
import time

appname = os.environ['APPNAME']
hostname = os.environ['HOSTNAME']
logsdir = f"/opt/{appname}/logs"
ftpdir = f"/opt/{appname}/ftp"
configsdir = f"/opt/{appname}/configs"
dhcp_report = pathlib.Path(f"{logsdir}/dhcp_report.csv")
xfer_report = pathlib.Path(f"{logsdir}/transfer_report.csv")
xfer_report2 = pathlib.Path(f"{ftpdir}/transfer_report.csv")
vendor_csv_file = pathlib.Path(f"{ftpdir}/vendor_class_defaults.csv")
ztp_csv_file = pathlib.Path(f"/opt/{appname}/ftp/ztp.csv")
dhcpd_config_file_loc = pathlib.Path('/etc/dhcp/dhcpd.conf')
ztp_log = pathlib.Path(f"{logsdir}/ztp.log")
ftp_log = pathlib.Path(f"{logsdir}/vsftpd_xfers.log")
device_models_json = pathlib.Path(f'{ftpdir}/supported_device_models.json')
prov_methods = pathlib.Path(f'{logsdir}/provisioning_methods.json')

vendor_csv_columns = ['hardware', 'vendor_cid', 'os', 'config']
report_csv_columns = columns = [
    'hardware', 'mac', 'os', 'config', 'ip',
    'os_xfer_msg', 'os_xfer_time', 'config_xfer_msg', 'config_xfer_time',
    'msg'
    ]
daemons = {'ftp': 'vsftpd', 'tftp': 'in.tftpd'}
xfer_oks = ['ok download', 'rrq']
xfer_errors = ['fail download', 'sending nak', 'connection refused']

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

def write_xfer_report(dhcp_objs, xfer_report, report_csv_columns):
    with open(xfer_report, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=report_csv_columns)
        writer.writeheader()
        writer.writerows(dhcp_objs)
    rval = subprocess.run(f"chown $HUID:$HGID {str(xfer_report)}", shell=True)

def hash_a_list(list_obj):
   return hash(json.dumps(list_obj))

def hash_changed(obj, lasthash):
    if hash_a_list(obj) == lasthash:
        return False
    else:
        return True

def follow_log(logfile):
    global lastupdate
    global lasthash
    print(f'[{dt.datetime.now()}] Start reading log file.')
    while True:
        line = logfile.readline()
        if not line:
            #print('waiting for new line...')
            if dt.datetime.now() >= lastupdate + dt.timedelta(seconds=2):
                lastupdate = dt.datetime.now()
                if hash_a_list(dhcp_objs) != lasthash:
                    lasthash = hash_a_list(dhcp_objs)
                    write_xfer_report(dhcp_objs, xfer_report, columns)
                    write_xfer_report(dhcp_objs, xfer_report2, columns)
                    print(f'[{now}] Wrote transfer report to file.')
            time.sleep(0.1)    # Sleep briefly
            continue
        yield line

# Start of main program
now = dt.datetime.now()
# Proper ISO 8601 time with local timezone info
isotime = now.astimezone().replace(microsecond=0).isoformat()

try:
    device_models = json.loads(device_models_json.read_text())
except:
    device_models_json = pathlib.Path(
        f'{configsdir}/supported_device_models.json'
        )
    device_models = json.loads(device_models_json.read_text())

if not all((dhcp_report.exists(), ztp_log.exists())):
    print(f"Error accessing `{dhcp_report}` or `{ztp_log}` file. Bye.")
    sys.exit()

# Read the vendor_class_defaults CSV
if not vendor_csv_file.exists():
    msg = f'[INFO] `{vendor_csv_file.name}` was not found.'
    print(msg)
    vendor_objs = [] # we still need the program to run
else:
    with open(vendor_csv_file) as f:
        t = f.readlines()
    reader_dict = csv.DictReader(t, fieldnames=vendor_csv_columns)
    original_vendor_columns = reader_dict.__next__()
    # List of the data objects
    vendor_objs = [row for row in reader_dict]

# Read the ZTP CSV (only to display a message on the transfer report)
if not ztp_csv_file.exists():
    msg = f'[INFO] `{ztp_csv_file.name}` was not found.'
    print(msg)

if not dhcp_report.exists():
    msg = f'[INFO] `{dhcp_report.name}` was not found.'
    print(msg)
    dhcp_objs = [] # we still need the program to run
else:
    # Read the dhcp_report CSV
    with open(dhcp_report) as f:
        t = f.readlines()
    reader_dict = csv.DictReader(t, fieldnames=report_csv_columns)
    original_report_columns = reader_dict.__next__()
    dhcp_objs = [row for row in reader_dict]

# Hardware look up table
hw_lut =  {
    each['config']: each['hardware']
    for each in vendor_objs if each['config']
        } | {
    each['os']: each['hardware']
    for each in vendor_objs if each['os']
        }

# dhcp lease regexes
dhcp_lease_search = (
    '(?P<mac>[0-9a-fA-F:]+)\s+(?P<ip>[0-9.]+)\s+(?P<hostname>[^\s]+)\s+.*'
    )
# dhcpd starting and ending ip search
dhcp_range_search = 'range\s+(?P<ip_start>[0-9.]+)\s+(?P<ip_end>[0-9.]+)'

# Find any dhcp_lease not in the static range
dhcpd_text = dhcpd_config_file_loc.read_text()
dhcp_range_match = re.search(dhcp_range_search, dhcpd_text)
ip_start = ipaddress.ip_address(dhcp_range_match['ip_start'])
ip_end = ipaddress.ip_address(dhcp_range_match['ip_end'])
write_xfer_report(dhcp_objs, xfer_report, report_csv_columns)
write_xfer_report(dhcp_objs, xfer_report2, report_csv_columns)
lastupdate = dt.datetime.now()
lasthash = hash_a_list(dhcp_objs)
dhcp_leases = get_dhcp_lease_list()
lasthash_dhcp_leases = hash_a_list(dhcp_leases)
if dhcp_leases:
    dhcp_objs = add_new_leases(dhcp_objs, dhcp_leases)

if prov_methods.exists():
    prov_enabled = json.loads(prov_methods.read_text())

daemons_alt = '|'.join([re.escape(d) for d in daemons.values()])
ip_lut = {item['ip']: item for item in dhcp_objs if item['ip']}
ips = ip_lut.keys()
ips_alt = '|'.join([re.escape(ip) for ip in ips])
re_ip = re.compile(
    f"(?P<protocol>{daemons_alt}).*\\b(?P<ip>{ips_alt})\\b"
    )
v_os_set = set([os for key in vendor_objs if  (os := key['os'])])
v_os_set_alt = '|'.join([re.escape(os) for os in v_os_set])
v_os = re.compile(f"(?P<os>{v_os_set_alt})")
v_conf_set = set([conf for key in vendor_objs if (conf := key['config'])])
v_conf_set_alt = '|'.join([re.escape(conf) for conf in v_conf_set])
v_conf = re.compile(f"(?P<config>{v_conf_set_alt})")

xfer_oks_alt = '|'.join([re.escape(m) for m in xfer_oks])
xfer_ok = re.compile(
    f'(?P<time>.*) (?:{hostname}).*(?P<fullmsg>(?P<msg>{xfer_oks_alt}).*'
    '(?P<type>config|os)(?:_files|_images).*)',
    re.IGNORECASE
    )
xfer_errors_alt = '|'.join([re.escape(m) for m in xfer_errors])
xfer_error = re.compile(
    f'(?P<time>.*) (?:{hostname}).*'
    f'(?P<fullmsg>(?P<msg>(?:{xfer_errors_alt})).*)',
    re.IGNORECASE
    )
xfer_types = '(?P<type>os|config)(?:_images|_files)'
xfer_type = re.compile(f'{xfer_types}')

with ztp_log.open() as f:
    for line in follow_log(f):
        # Add any unknown dhcp requests
        dhcp_leases = get_dhcp_lease_list()
        if dhcp_leases and hash_changed(dhcp_leases, lasthash_dhcp_leases):
            lasthash_dhcp_leases = hash_a_list(dhcp_leases)
            dhcp_objs = add_new_leases(dhcp_objs, dhcp_leases)
            ip_lut = {item['ip']: item for item in dhcp_objs if item['ip']}
            ips = ip_lut.keys()
            ips_alt = '|'.join([re.escape(ip) for ip in ips])
            re_ip = re.compile(
                f"(?P<protocol>{daemons_alt}).*\\b(?P<ip>{ips_alt})\\b"
                )
        # Search for one of our IPs in the current line of syslog
        if (res := re_ip.search(line)):
            item = ip_lut[res['ip']]
            if (okmsg := xfer_ok.search(line)):
                # fill in mising info for vendor class dynamic dhcp
                if ipaddress.ip_address(item['ip']) >= ip_start:
                    if (okmsg['type'] == 'config'
                        and (file := v_conf.search(line))):
                        # dynamic dhcp client from vendor class id
                        item['config'] = file['config']
                        if file['config'] in hw_lut:
                            item['hardware'] = hw_lut[file['config']]
                    if (okmsg['type'] == 'os'
                        and (file := v_os.search(line))):
                        # dynamic dhcp client from vendor class id
                        item['os'] = file['os']
                        if file['os'] in hw_lut:
                            item['hardware'] = hw_lut[file['os']]
                if okmsg['type'] == 'config' and item['config'] in line:
                    if item['config_xfer_msg']:
                        # maybe repeated transfer
                        item['config_xfer_msg'] += '\n' + okmsg['msg']
                    else:
                        item['config_xfer_msg'] = okmsg['msg']
                    if item['config_xfer_time']:
                        # maybe repeated transfer
                        item['config_xfer_time'] += '\n' + okmsg['time']
                    else:
                        item['config_xfer_time'] = okmsg['time']
                elif okmsg['type'] == 'os' and item['os'] in line:
                    if item['os_xfer_msg']:
                        # maybe repeated transfer
                        item['os_xfer_msg'] += '\n' + okmsg['msg']
                    else:
                        item['os_xfer_msg'] = okmsg['msg']
                    if item['os_xfer_time']:
                        # maybe repeated transfer
                        item['os_xfer_time'] += '\n' + okmsg['time']
                    else:
                        item['os_xfer_time'] = okmsg['time']
                elif okmsg['type'] == 'config':
                    if item['msg']:
                        item['msg'] += '. ' + okmsg['fullmsg']
                    else:
                        item['msg'] = okmsg['fullmsg']
                elif okmsg['type'] == 'os':
                    if item['msg']:
                        item['msg'] += '. ' + okmsg['fullmsg']
                    else:
                        item['msg'] = okmsg['fullmsg']
                else:
                    if item['msg']:
                        item['msg'] += '. ' + okmsg['fullmsg']
                    else:
                        item['msg'] = okmsg['fullmsg']
            elif (errmsg := xfer_error.search(line)):
                if (tmsg := xfer_type.search(errmsg['fullmsg'])):
                    # fill in mising info for vendor class dynamic dhcp
                    if ipaddress.ip_address(item['ip']) >= ip_start:
                        if (tmsg['type'] == 'config'
                            and (file := v_conf.search(line))):
                            # dynamic dhcp client from vendor class id
                            item['config'] = file['config']
                            if file['config'] in hw_lut:
                                item['hardware'] = hw_lut[file['config']]
                        if (tmsg['type'] == 'os'
                            and (file := v_os.search(line))):
                            # dynamic dhcp client from vendor class id
                            item['os'] = file['os']
                            if file['os'] in hw_lut:
                                item['hardware'] = hw_lut[file['os']]
                    if tmsg['type'] == 'config' and item['config'] in line:
                        if item['config_xfer_msg']:
                            # maybe repeated transfer
                            item['config_xfer_msg'] += '\n' + errmsg['msg']
                        else:
                            item['config_xfer_msg'] = errmsg['msg']
                        if item['config_xfer_time']:
                            # maybe repeated transfer
                            item['config_xfer_time'] += '\n' + errmsg['time']
                        else:
                            item['config_xfer_time'] = errmsg['time']
                    elif tmsg['type'] == 'os' and item['os'] in line:
                        if item['os_xfer_msg']:
                            # maybe repeated transfer
                            item['os_xfer_msg'] += '\n' + errmsg['msg']
                        else:
                            item['os_xfer_msg'] = errmsg['msg']
                        if item['os_xfer_time']:
                            # maybe repeated transfer
                            item['os_xfer_time'] += '\n' + errmsg['time']
                        else:
                            item['os_xfer_time'] = errmsg['time']
                    elif tmsg['type'] == 'config':
                        if item['msg']:
                            item['msg'] += '. ' + errmsg['fullmsg']
                        else:
                            item['msg'] = errmsg['fullmsg']
                    elif tmsg['type'] == 'os':
                        if item['msg']:
                            item['msg'] += '. ' + errmsg['fullmsg']
                        else:
                            item['msg'] = errmsg['fullmsg']
                    else:
                        if item['msg']:
                            item['msg'] += '. ' + errmsg['fullmsg']
                        else:
                            item['msg'] = errmsg['fullmsg']
                # tftp sends messages on multiple lines
                # a bad file name will have the same time stamp
                elif re.search(errmsg['time'], item['config_xfer_time']):
                    # matches the previous config transfer message
                    item['config_xfer_msg'] += '\n' + 'Error'
                    item['config_xfer_time'] += '\n' + errmsg['time']
                    item['msg'] += '. ' + errmsg['fullmsg']
                elif re.search(errmsg['time'], item['os_xfer_time']):
                    # matches the previous os transfer message
                    item['os_xfer_msg'] += '\n' + 'Error'
                    item['os_xfer_time'] += '\n' + errmsg['time']
                    item['msg'] += '. ' + errmsg['fullmsg']
                else:
                    # Not a config or os file in msg or previous complete
                    if item['msg']:
                        item['msg'] += (
                            f". {errmsg['time']} {errmsg['fullmsg']}"
                            )
                    else:
                        item['msg'] = (
                            f"{errmsg['time']} {errmsg['fullmsg']}"
                            )
            else:
                # some other syslog message
                pass
            # try to avoid looking up the protocol, if possible
            if res['protocol'] == daemons['ftp']:
                pass
            elif res['protocol'] == daemons['tftp']:
                pass
            else:
                # maybe a dhcp message or some other syslog msg
                pass
