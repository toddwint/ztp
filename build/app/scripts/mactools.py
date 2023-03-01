#!/usr/bin/env python3
#!python3
"""
This tool includes functions to handle Ethernet MAC addresses.
"""

__author__ = 'Todd Wintermute'
__version__ = '0.0.2'
__date__ = '2023-02-28'

import re
import pathlib
import string

def remove_separators(mac):
    """Takes a hex MAC string.
    Returns string with removed separating and white space characters.
    """
    xmac = re.sub('[ :.-]', '', mac)
    return xmac

def std_mac_format(mac, sep=':'):
    """Takes a hexadecimal MAC string. Returns string with separators."""
    strmac = f'{sep}'.join(
        re.findall('.{1,2}', f'{remove_separators(mac):0>12}')
        )
    return strmac

def std_oui_format(oui, sep=':'):
    """Takes a hex OUI string. Returns string with separators."""
    stroui = f'{sep}'.join(
        re.findall('.{1,2}', f'{remove_separators(oui):0>6}')
        )
    return stroui

def is_mac(mac):
    """Takes a hex MAC string. Validates it is a MAC."""
    xmac = remove_separators(mac)
    if not all([(char in string.hexdigits) for char in xmac]):
        return False
    if len(xmac) != 12:
        return False
    intmac = int(xmac, base=16)
    if intmac < 0 or intmac > 0xffffffffffff:
        return False
    return True

def is_oui(oui):
    """Takes a hex OUI string. Validates it is on OUI"""
    xoui = remove_separators(oui)
    if not all([char in string.hexdigits for char in xoui]):
        return False
    if len(xoui) != 6:
        return False
    intoui = int(xoui, base=16)
    if intoui < 0 or intoui > 0xffffff:
        return False
    return True

def is_unicast(mac):
    """Takes a hex MAC string. Returns True if unicast/individual"""
    xmac = remove_separators(mac)
    intmac = int(xmac, base=16)
    testbit = 0x010000000000
    if intmac & testbit == testbit:
        return False
    return True

def is_multicast(mac):
    """Takes a hex MAC string. Returns True if multicast/group."""
    xmac = remove_separators(mac)
    intmac = int(xmac, base=16)
    testbit = 0x010000000000
    if intmac & testbit != testbit:
        return False
    return True

def is_universal(mac):
    """Takes a hex MAC string. Returns True if universal."""
    xmac = remove_separators(mac)
    intmac = int(xmac, base=16)
    testbit = 0x020000000000
    if intmac & testbit == testbit:
        return False
    return True

def is_local(mac):
    """Takes a hex MAC string. Returns True if local."""
    xmac = remove_separators(mac)
    intmac = int(xmac, base=16)
    testbit = 0x020000000000
    if intmac & testbit != testbit:
        return False
    return True

def incr_mac(mac, step=1):
    """Takes a hex MAC string. Returns incremented value if possible."""
    xmac = remove_separators(mac)
    intmac = int(xmac, base=16)
    intnextmac = intmac + step
    xnextmac = format(intnextmac, 'x')
    nextmac = std_mac_format(xnextmac)
    if not is_mac(nextmac):
        raise ValueError('Calculated MAC is not a MAC address.')
    return nextmac

def decr_mac(mac, step=1):
    """Takes a hex MAC string. Returns decremented value if possible."""
    xmac = remove_separators(mac)
    intmac = int(xmac, base=16)
    intprevmac = intmac - step
    xprevmac = format(intprevmac, 'x')
    prevmac = std_mac_format(xprevmac)
    if not is_mac(prevmac):
        raise ValueError('Calculated MAC is not a MAC address.')
    return prevmac

def get_oui_from_mac(mac):
    """Takes a hex MAC string. Returns OUI portion without separators."""
    oui = remove_separators(mac)[:6]
    return oui

def get_oui_as_mac(oui):
    """Takes a hex OUI string. Returns MAC using zeros without separators"""
    strmac = f'{remove_separators(oui):0<12}'
    return strmac

def find_oui_org(oui):
    """__Experimental__
    Takes a hex OUI string. Returns organization name if found.
    Requires oui.txt file.
    """
    oui = (oui).upper()
    # Download from <https://standards-oui.ieee.org/oui/oui.txt>
    # curl -O https://standards-oui.ieee.org/oui/oui.txt
    ieee_oui_list = pathlib.Path('oui.txt')
    if not ieee_oui_list.exists():
        raise Exception(
        f'''File `{ieee_oui_list.absolute()}` not found.
Download from https://standards-oui.ieee.org/oui/oui.txt
`curl -O https://standards-oui.ieee.org/oui/oui.txt`'''
        )
    with open(ieee_oui_list, encoding='utf-8') as f:
        t = f.read()
    m = re.search(f'{oui}.*\\t+(?P<oui_org>.*)', t)
    if not m or not m['oui_org']:
        return f'unknown'
    return m['oui_org']

def find_mac_org(mac):
    """__Experimental__
    Takes a hex MAC string. Returns organization name if found.
    Requires oui.txt file.
    """
    oui = get_oui_from_mac(mac)
    mac_org = find_oui_org(oui)
    return mac_org

def find_org_ouis(orgname):
    """__Experimental__
    Takes an organization name or partial organization name.
    Returns a list of OUI(s) that organization owns.
    Requires oui.txt file.
    """
    ieee_oui_list = pathlib.Path('oui.txt')
    if not ieee_oui_list.exists():
        raise Exception(
        f'''File `{ieee_oui_list.absolute()}` not found.
Download from https://standards-oui.ieee.org/oui/oui.txt
`curl -O https://standards-oui.ieee.org/oui/oui.txt`'''
        )
    with open(ieee_oui_list, encoding='utf-8') as f:
        t = f.read()
    m = re.findall(f'([0-9A-Fa-f]{{6}}).*\\t+.*{orgname}.*', t)
    if not m:
        return f'unknown'
    return m

if __name__ == '__main__':
    print(__doc__)
