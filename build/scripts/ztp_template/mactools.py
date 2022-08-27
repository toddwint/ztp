#!/usr/bin/env python3
#!python3
'''
This tool includes functions to handle Ethernet MAC addresses.
'''

import re
import pathlib
import string

def remove_separators(mac: str) -> str:
    '''Takes various types of MACs and removes separating and whitespace characters.'''
    xmac = re.sub('[ :.-]', '', mac)
    return xmac

def convert_to_str(mac: int | str, sep: str = ':') -> str:
    '''Takes an integer or hexadecimal string and adds in separators.'''
    if type(mac) == int:
        strmac = f'{sep}'.join(re.findall('.{1,2}', f'{mac:012x}'))
    elif type(mac) == str:
        base = 16
        numbases = ['0b', '0o', '0x']
        if any([mac.startswith(x) for x in numbases]):
            base = 0
        strmac = f'{sep}'.join(re.findall('.{1,2}', f'{convert_to_int(mac, base=base):012x}'))
    else:
        raise TypeError('Type(int|str) not received.')
    if not is_mac(strmac):
        raise Exception('Supplied value is not a MAC address.')
    return strmac

def convert_to_hex(mac: int | str, sep: str = '') -> str:
    '''Takes in a MAC and returns the hexadecimal representation of that value.'''
    return convert_to_str(mac, sep=sep)

def convert_to_int(mac: str, base: int = 16) -> int:
    '''Takes in a MAC and returns the integer representation of that value.'''
    if type(mac) == str:
        numbases = ['0b', '0o', '0x']
        if any([mac.startswith(x) for x in numbases]):
            base = 0
        intmac = int(remove_separators(mac), base=base)
    else:
        raise TypeError('Type(str) not received.')
    return intmac

def convert_to_bin(mac: int | str, base: int = 16) -> str:
    '''Takes in a MAC and returns the binary string representation of that value.'''
    if type(mac) == int:
        binmac = f'{mac:048b}'
    elif type(mac) == str:
        numbases = ['0b', '0o', '0x']
        if any([mac.startswith(x) for x in numbases]):
            base = 0
        binmac = f'{convert_to_int(mac, base=base):048b}'
    else:
        raise TypeError('Type(str) not received.')
    return binmac

def is_mac(mac: str) -> bool:
    '''Takes in a MAC and checks it against various tests to determine if it is valid.'''
    xmac = remove_separators(mac)
    if False in [char in string.hexdigits for char in xmac]:
        return False
    if len(xmac) != 12:
        return False
    intmac = convert_to_int(mac)
    if intmac < 0 or intmac > 0xffffffffffff:
        return False
    return True

def is_oui(oui: str) -> bool:
    '''Takes in an OUI and checks it against various tests to determine if it is valid.'''
    xoui = remove_separators(oui)
    if False in [char in string.hexdigits for char in xoui]:
        return False
    if len(xoui) != 6:
        return False
    intoui = convert_to_int(oui)
    if intoui < 0 or intoui > 0xffffff:
        return False
    return True

def is_unicast(mac: str) -> bool:
    '''Takes in a MAC and compares it to determine if it is unicast/individual.'''
    if not is_mac(mac):
        raise ValueError('This is not a correct mac: {mac}')
    intmac = convert_to_int(mac)
    testbit = 0x010000000000
    if intmac & testbit == testbit:
        return False
    return True

def is_multicast(mac: str) -> bool:
    '''Takes in a MAC and compares it to determine if it is multicast/group.'''
    if not is_mac(mac):
        raise ValueError('This is not a correct mac: {mac}')
    intmac = convert_to_int(mac)
    testbit = 0x010000000000
    if intmac & testbit != testbit:
        return False
    return True

def is_universal(mac: str) -> bool:
    '''Takes in a MAC and compares it to determine if it is universal.'''
    if not is_mac(mac):
        raise ValueError('This is not a correct mac: {mac}')
    intmac = convert_to_int(mac)
    testbit = 0x020000000000
    if intmac & testbit == testbit:
        return False
    return True

def is_local(mac: str) -> bool:
    '''Takes in a MAC and compares it to determine if it is local.'''
    if not is_mac(mac):
        raise ValueError('This is not a correct mac: {mac}')
    intmac = convert_to_int(mac)
    testbit = 0x020000000000
    if intmac & testbit != testbit:
        return False
    return True
    
def incr_mac(mac: str, step: int = 1) -> str:
    '''Takes in a MAC and increments it to the next value.'''
    if not is_mac(mac):
        raise ValueError('MAC provided is incorrect.')
    intnextmac = convert_to_int(mac) + step
    nextmac = convert_to_str(intnextmac)
    if not is_mac(nextmac):
        raise ValueError('Calculated MAC is not a MAC address.')
    return nextmac

def decr_mac(mac: str, step: int = 1) -> str:
    '''Takes in a MAC and decrements it to the next value.'''
    if not is_mac(mac):
        raise ValueError('MAC provided is incorrect.')
    intprevmac = convert_to_int(mac) - step
    prevmac = convert_to_str(intprevmac)
    if not is_mac(prevmac):
        raise ValueError('Calculated MAC is not a MAC address.')
    return prevmac

def get_oui(mac: str) -> str:
    '''Takes a MAC and returns the OUI portion.'''
    oui = remove_separators(mac)[:6]
    if not is_oui(oui):
        raise ValueError('This is not a correct oui: {oui}')
    return oui.upper()

def find_oui_org(mac: str) -> str:
    '''Takes a OUI and searches for the owning organization name.'''
    oui = get_oui(mac).upper()
    # Download from <https://standards-oui.ieee.org/oui/oui.txt>
    # curl -O https://standards-oui.ieee.org/oui/oui.txt
    ieee_oui_list = pathlib.Path('oui.txt')
    if not ieee_oui_list.exists():
        raise Exception(
        f'''File `{ieee_oui_list}` not found.
Download from https://standards-oui.ieee.org/oui/oui.txt
`curl -O https://standards-oui.ieee.org/oui/oui.txt`'''
        )
    with open(ieee_oui_list, encoding='utf-8') as f:
        t = f.read()
    m = re.search(f'{oui}.*\\t+(?P<oui_org>.*)', t)
    if not m or not m['oui_org']:
        return f'Could not find Organization for {oui}.'
    return m['oui_org']

def find_org_ouis(orgname: str) -> str: 
    '''Takes organization name or partial organization name and searches for the owning OUI(s).'''
    ieee_oui_list = pathlib.Path('oui.txt')
    if not ieee_oui_list.exists():
        raise Exception(
        f'''File `{ieee_oui_list}` not found.
Download from https://standards-oui.ieee.org/oui/oui.txt
`curl -O https://standards-oui.ieee.org/oui/oui.txt`'''
        )
    with open(ieee_oui_list, encoding='utf-8') as f:
        t = f.read()
    m = re.findall(f'([0-9A-Fa-f]{{6}}).*\\t+.*{orgname}.*', t)
    if not m:
        return f'Could not find OUIs for {orgname}.'
    return m

if __name__ == '__main__':
    print(__doc__)
