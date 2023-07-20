#!/usr/bin/env python3
"""
Tools for obtaining IP information like broadcast, network, etc.
"""

__author__ = 'Todd Wintermute'
__version__ = '0.0.3'
__date__ = '2023-07-10'

import argparse
import ipaddress
import re
import sys

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
        'subnet',
        nargs='*',
        type=str,
        help=(
            'IP subnet. Separate with a slash "/" or space. '
            '(examples: 192.168.10.0/24 or 192.168.10.0 255.255.255.0)'
            ),
        )
    filter_keys = (
            'network', 'netmask', 'netmaskbits', 'networkaddr',
            'broadcast', 'hostmin', 'hostmax', 'numhosts'
            )
    parser.add_argument(
        '-f', '--filter',
        choices=filter_keys,
        action='append',
        metavar='key',
        help=(
            f'Enter one or more `key(s)` to filter the output. '
            f'Omitting this option shows all keys.  Keys are: {filter_keys}'
            ),
        )
    return parser

def interactive_mode():
    subnet = input('Enter subnet or `q` to quit: ')
    if subnet.lower().startswith('q'):
        print('Bye!')
        sys.exit()
    if not subnet:
        print('Input not detected.')
        interactive_mode()
    subnet = subnet.split()
    print_subnet_info(subnet, None)
    interactive_mode()

def print_subnet_info(subnet, filters):
    subnet = ' '.join(subnet)
    subnet = re.sub('(\s|/)+', '/', subnet)
    network = ipaddress.ip_network(subnet, strict=False)
    netmask = network.netmask
    netmaskbits = network.prefixlen
    networkaddr = network.network_address
    broadcast = network.broadcast_address
    hostmin = networkaddr + 1
    hostmax = broadcast - 1
    total_hosts = network.num_addresses - 2
    items = {
        'network': f'Network:      {network}',
        'netmask': f'Netmask:      {netmask}', 
        'netmaskbits': f'Netmask_Bits: {netmaskbits}', 
        'networkaddr': f'Network_Addr: {networkaddr}',
        'hostmin': f'Host_Min:     {hostmin}', 
        'hostmax': f'Host_Max:     {hostmax}',
        'broadcast': f'Broadcast:    {broadcast}',
        'numhosts': f'Total_Hosts:  {total_hosts}',
        }
    if filters:
        for each in filters:
            print(items[each])
    else:
        for each in items:
            print(items[each])

def main():
    global args
    parser = parse_arguments()
    args = parser.parse_args()
    if not args.subnet:
        interactive_mode()
    else:
        print_subnet_info(args.subnet, args.filter)

if __name__ == '__main__':
    main()
