#!/usr/bin/env python3
"Print transfer report to the screen after 2s intervals if update is found"

__version__ = '0.0.1'
__author__ = 'Todd Wintermute'
__date__ = '2023-07-20'

import csv
import datetime as dt
import json
import os
import pathlib
import subprocess
import time

appname = os.environ['APPNAME']
xfer_report = pathlib.Path(f"/opt/{appname}/logs/transfer_report.csv")
report_csv_columns = [
    'hardware', 'mac', 'os', 'config', 'ip',
    'os_xfer_msg', 'os_xfer_time', 'config_xfer_msg', 'config_xfer_time',
    'msg'
    ]
prov_methods = pathlib.Path(f'/opt/{appname}/logs/provisioning_methods.json')
prov_enabled = json.loads(prov_methods.read_text())
prov_msg = (
    "Provision using Vendor Class ID method: "
        f"{prov_enabled['vendor_class_id_method']}"
    "\n"
    "Provision using MAC ADDR method: "
        f"{prov_enabled['mac_addr_method']}"
    )

def hash_a_list(list_obj):
   return hash(json.dumps(list_obj))

def read_xfer_report():
    if not xfer_report.exists():
        msg = f'[INFO] `{xfer_report.name}` was not found.'
        print(msg)
        report_objs = [] # we still need the program to run
    else:
        with open(xfer_report) as f:
            t = f.readlines()
        reader_dict = csv.DictReader(t, fieldnames=report_csv_columns)
        original_report_columns = reader_dict.__next__()
        report_objs = [row for row in reader_dict]
    return report_objs

def report_changed(report_objs):
    if hash_a_list(report_objs) == lasthash:
        return False
    else:
        return True

def print_report():
    ret = subprocess.run('clear', shell=True)
    ret = subprocess.run(
        ['tmux', 'list-sessions'],
        capture_output=True,
        universal_newlines=True
        )
    if not ret.returncode:
        ret = subprocess.run('tmux clear-history -t 1', shell=True)
    ret = subprocess.run(
        f'column.py {xfer_report}',
        shell=True,
        capture_output=True,
        universal_newlines=True
        )
    if not ret.returncode:
        print(ret.stdout)
    else:
        print('Some error occurred')

def main():
    global lasthash
    global lastupdate
    global report_objs
    report_objs = read_xfer_report()
    lasthash = hash_a_list(report_objs)
    lastupdate = dt.datetime.now()
    print_report()
    print(prov_msg)
    print(f'Last updated at {lastupdate}')
    while True:
        if dt.datetime.now() >= lastupdate + dt.timedelta(seconds=5):
            lastupdate = dt.datetime.now()
            report_objs = read_xfer_report()
            if report_changed(report_objs):
                lasthash = hash_a_list(report_objs)
                print_report()
                print(prov_msg)
                print(f'Last updated at {lastupdate}')
        else:
            time.sleep(0.1)

if __name__ == '__main__':
    main()
