#!/usr/bin/env python3
'''Tools for obtaining IP information like broadcast, network, etc.'''

__author__ = 'Todd Wintermute'
__version__ = '0.0.2'
__date__ = '2023-02-27'

import argparse
import ipaddress

parser = argparse.ArgumentParser(
    description = __doc__,
    epilog = 'Have a great day!',
    )
parser.add_argument(
    '-v', '--version',
    help = 'show the version number and exit',
    action = 'version',
    version= f'Version: %(prog)s  {__version__}  ({__date__})',
    )
parser.add_argument(
    'subnet',
    type = str,
    help = f'IP subnet (example: 192.168.10.0/24)',
    )
filter_keys = (
        'network', 'netmask', 'netmaskbits', 'networkaddr',
        'broadcast', 'hostmin', 'hostmax', 'numhosts'
        )
parser.add_argument(
    '-f', '--filter',
    choices = filter_keys,
    type = str,
    nargs = '*',
    default = False,
    metavar = 'key',
    help = f'''Enter one or more `key(s)` to filter the output. \
Omitting this option shows all keys.
Keys are: {filter_keys}''',
    )
args = parser.parse_args()

subnet = args.subnet
network = ipaddress.ip_network(subnet, strict=False)
netmask = network.netmask
netmaskbits = network.prefixlen
networkaddr = network.network_address
broadcast = network.broadcast_address
hostmin = networkaddr + 1
hostmax = broadcast -1
total_hosts = network.num_addresses - 2

items = {
    'network': f'Network:      {network}',
    'netmask': f'Netmask:      {netmask}', 
    'netmaskbits': f'Netmask_Bits: {netmaskbits}', 
    'networkaddr': f'Network_Addr: {networkaddr}',
    'hostmin': f'Host_Min:     {hostmin}', 
    'hostmax': f'Host_Max:     {hostmax}',
    'broadcast': f'Broadcast:    {broadcast}',
    'numhosts': f'Total Hosts:  {total_hosts}',
    }

if args.filter:
    for each in args.filter:
        print(items[each])
else:
    for each in items:
        print(items[each])
