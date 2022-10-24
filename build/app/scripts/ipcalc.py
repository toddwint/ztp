#!/usr/bin/env python3
'''Tools for obtaining IP information like broadcast, network, etc.'''
__version__ = '0.0.1'

import argparse
import ipaddress

parser = argparse.ArgumentParser(
    description=__doc__,
    epilog='Have a great day!',
    )
parser.add_argument(
    '-v', '--version',
    help='show the version number and exit',
    action='version',
    version=f'Version: {__version__}',
    )
parser.add_argument(
    'subnet',
    type=str,
    help=f'IP subnet (example: 192.168.10.0/24)',
    )
parser.add_argument(
    '-f', '--filter',
    choices=['network', 'netmask', 'netmaskbits', 'networkaddr', 'broadcast', 'hostmin', 'hostmax'],
    type=str,
    nargs='*',
    default=False,
    help=f'Enter one or more of the choices to filter the output. Default shows all fields.',
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

choices = {
    'network': f'Network:      {network}',
    'netmask': f'Netmask:      {netmask}', 
    'netmaskbits': f'Netmask_Bits: {netmaskbits}', 
    'networkaddr': f'Network_Addr: {networkaddr}',
    'hostmin': f'Host_Min:     {hostmin}', 
    'hostmax': f'Host_Max:     {hostmax}',
    'broadcast': f'Broadcast:    {broadcast}', 
    }

if args.filter:
    for each in args.filter:
        print(choices[each])
else:
    for each in choices:
        print(choices[each])
