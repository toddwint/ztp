#!/usr/bin/env python3
#!python3
'''
This program takes a mac address, sends it to mactools.incr_mac(mac)
and then returns the next mac address.
'''

import mactools

if __name__ == '__main__':
    print(__doc__)
    mac = input('Please enter a MAC address: ')
    newmac = mactools.incr_mac(mac)
    print(f'The next MAC address is: {newmac}')
