#!/usr/bin/env python3
"""Create a menu.json needed to run menu script"""

__version__ = '0.0.1'
__date__ = '2023-12-22'
__author__ = 'Todd Wintermute'

import argparse
import json
import os
import pathlib

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='Have a great day!',
        )
    parser.add_argument(
        '-v', '--version',
        help='show the version number and exit',
        action='version',
        version=f'Version: %(prog)s  {__version__}  ({__date__})',
        )
    parser.add_argument(
        'outfile',
        nargs='?',
        type=pathlib.Path,
        default='./menu.json',
        help=(
            'Optional location where to write the json file. '
            'Default is `./menu.json`'
            ),
        )
    return parser

def dump_json(menulist, output):
    if not output.exists():
        output.touch()
    with open(output, 'w') as f:
        json.dump(menulist, f, indent=1)

if __name__ == '__main__':
    appname = os.environ['APPNAME']
    tailcmd = "tail -F -n +1"
    #fzfcmd = "fzf --tac --reverse --no-sort"
    fzfcmd = "fzf --tac --no-sort"
    fzfcmd2 = "fzf --reverse --no-sort"
    logsdir = f"/opt/{appname}/logs"
    logsdir2 = f"/opt/{appname}/logs/ntpstats"
    ftpdir = f"/opt/{appname}/ftp"
    debugdir = f"/opt/{appname}/debug"
    menu_log_fzf = [
        ("transfer report", f"column.py {logsdir}/transfer_report.csv | {fzfcmd2} --header-lines=1"),
        (f"{appname} log (syslog)", f"{tailcmd} {logsdir}/{appname}.log | {fzfcmd}"),
        ("ftp transfers", f"{tailcmd} {logsdir}/vsftpd_xfers.log | {fzfcmd2}"),
        ("tftp transfers", f"""{tailcmd} {logsdir}/{appname}.log | {fzfcmd2} --query="'in.tftpd " """),
        ("ntp rawstats", f"{tailcmd} {logsdir2}/rawstats | {fzfcmd}"),
        ("ntp peerstats", f"{tailcmd} {logsdir2}/peerstats | {fzfcmd}"),
        ("ntp loopstats", f"{tailcmd} {logsdir2}/loopstats | {fzfcmd}"),
        ("ntp sysstats", f"{tailcmd} {logsdir2}/sysstats | {fzfcmd}"),
        ("ntp clockstats", f"{tailcmd} {logsdir2}/clockstats | {fzfcmd}"),
        ]
    menu_log = [
        ("transfer report", f"column.py {logsdir}/transfer_report.csv | more"),
        (f"{appname} log (syslog)", f"more {logsdir}/{appname}.log"),
        ("ftp transfers", f"more {logsdir}/vsftpd_xfers.log"),
        ("tftp transfers", f"grep 'in.tftpd' {logsdir}/{appname}.log | more"),
        ("ntp rawstats", f"more {logsdir2}/rawstats"),
        ("ntp peerstats", f"more {logsdir2}/peerstats"),
        ("ntp loopstats", f"more {logsdir2}/loopstats"),
        ("ntp sysstats", f"more {logsdir2}/sysstats"),
        ("ntp clockstats", f"more {logsdir2}/clockstats"),
        ]
    menu_configuration = [
        ("ztp.csv", f"column.py {ftpdir}/ztp.csv | more"),
        ("vendor_class_defaults.csv", f"column.py {ftpdir}/vendor_class_defaults.csv | more"),
        ("supported_device_models.json", f"more {ftpdir}/supported_device_models.json"),
        ("provisioning_methods.json", f"more {logsdir}/provisioning_methods.json"),
        ("dhcpd", "more /etc/dhcp/dhcpd.conf"),
        ("vsftpd", "more /etc/vsftpd.conf"),
        ("tftpd-hpa", "more /etc/default/tftpd-hpa"),
        ("webfsd", "more /etc/webfsd.conf"),
        ("ntp", "more /etc/ntp.conf"),
        ("IP addresses", "ip addr show | more"),
        ("Routing table", "ip route show | more"),
        ("ARP or NDISC cache", "ip neighbor show | more"),
        ("Network devices", "ip link show | more"),
        ]
    menu_debug = [
        ("Save transfer report", f"{debugdir}/save_transfer_report.sh"),
        ("Other dhcp leases", f"dhcp-lease-list"),
        ("Generate DHCPD configuration", f"{debugdir}/generate_dhcpd_conf.sh"),
        (f"Show {appname} services", f"{debugdir}/services_status.sh"),
        ("Show processes", f"ps ax | more"),
        ("Show sockets", f"ss --all --numeric --processes | more"),
        #("ttyd log", f"more {logsdir}/ttyd.log"),
        ("ttyd1 log", f"more {logsdir}/ttyd1.log"),
        ("ttyd2 log", f"more {logsdir}/ttyd2.log"),
        ("frontail log", f"more {logsdir}/frontail.log"),
        ("tailon log", f"more {logsdir}/tailon.log"),
        ("generate_transfer_report.log", f"more {logsdir}/generate_transfer_report.log"),
        ]
    menu = [
        ("Launch tmux", f"/opt/{appname}/scripts/tmux.sh"),
        ("Watch transfer report", f"/opt/{appname}/scripts/transfer_report.py"),
        ("Search logs", menu_log_fzf),
        ("View logs", menu_log),
        ("View configuration", menu_configuration),
        ("Debug scripts", menu_debug),
        ]
    parser = parse_arguments()
    args = parser.parse_args()
    dump_json(menu, args.outfile)
