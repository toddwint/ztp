#!/usr/bin/env python3
#!python3
'''
Unit testing for mactools module/script
'''

import mactools

mac1 = '4ccc34.121212'
mac2 = 'ffffff.ffffff'
mac3 = 'f1:ff:ff:ff:ff:ff'
mac4 = '00-09-0F-AA-00-01'
mac5 = 'E8-D8-D1-3A-40-30'
mac6 = '24-41-8C-CE-A6-54'
badmac1 = '00-00-00-AB-CD-FG'

oui1 = '4ccc34'
oui2 = mactools.get_oui(mac1)
oui3 = '24-41-8c'
oui4 = 'ffffff'
oui5 = '00:09:0f'
oui6 = 'f1.ff.ff'
badoui1 = 'f1.f2.fg'

# mac1
assert mactools.is_unicast(mac1) == True
assert mactools.is_multicast(mac1) == False
assert mactools.is_universal(mac1) == True
assert mactools.is_local(mac1) == False

# mac2
assert mactools.is_unicast(mac2) == False
assert mactools.is_multicast(mac2) == True
assert mactools.is_universal(mac2) == False
assert mactools.is_local(mac2) == True

# mac3
assert mactools.is_unicast(mac3) == False
assert mactools.is_multicast(mac3) == True
assert mactools.is_universal(mac3) == True
assert mactools.is_local(mac3) == False

# mac4
assert mactools.is_unicast(mac4) == True
assert mactools.is_multicast(mac4) == False
assert mactools.is_universal(mac4) == True
assert mactools.is_local(mac4) == False

# mac5
assert mactools.is_unicast(mac5) == True
assert mactools.is_multicast(mac5) == False
assert mactools.is_universal(mac5) == True
assert mactools.is_local(mac5) == False

# mac6
assert mactools.is_unicast(mac6) == True
assert mactools.is_multicast(mac6) == False
assert mactools.is_universal(mac6) == True
assert mactools.is_local(mac6) == False

assert mactools.is_mac(mac1) == True
assert mactools.is_mac(mac2) == True
assert mactools.is_mac(mac3) == True
assert mactools.is_mac(mac4) == True
assert mactools.is_mac(mac5) == True
assert mactools.is_mac(mac6) == True
assert mactools.is_mac(badmac1) == False
assert mactools.is_mac(oui1) == False
assert mactools.is_mac(oui2) == False
assert mactools.is_mac(oui3) == False
assert mactools.is_mac(oui4) == False
assert mactools.is_mac(oui5) == False
assert mactools.is_mac(oui6) == False
assert mactools.is_mac(badoui1) == False

assert mactools.is_oui(mac1) == False
assert mactools.is_oui(mac2) == False
assert mactools.is_oui(mac3) == False
assert mactools.is_oui(mac4) == False
assert mactools.is_oui(mac5) == False
assert mactools.is_oui(mac6) == False
assert mactools.is_oui(badmac1) == False
assert mactools.is_oui(oui1) == True
assert mactools.is_oui(oui2) == True
assert mactools.is_oui(oui3) == True
assert mactools.is_oui(oui4) == True
assert mactools.is_oui(oui5) == True
assert mactools.is_oui(oui6) == True
assert mactools.is_oui(badoui1) == False

assert mactools.convert_to_str(mac1) == '4c:cc:34:12:12:12'
assert mactools.convert_to_str(mac2) == 'ff:ff:ff:ff:ff:ff'
assert mactools.convert_to_str(mac3) == 'f1:ff:ff:ff:ff:ff'
assert mactools.convert_to_str(mac4) == '00:09:0f:aa:00:01'
assert mactools.convert_to_str(mac5) == 'e8:d8:d1:3a:40:30'
assert mactools.convert_to_str(mac6) == '24:41:8c:ce:a6:54'

assert mactools.convert_to_hex(mac1) == '4ccc34121212'
assert mactools.convert_to_hex(mac2) == 'ffffffffffff'
assert mactools.convert_to_hex(mac3) == 'f1ffffffffff'
assert mactools.convert_to_hex(mac4) == '00090faa0001'
assert mactools.convert_to_hex(mac5) == 'e8d8d13a4030'
assert mactools.convert_to_hex(mac6) == '24418ccea654'

assert mactools.convert_to_int(mac1) == 84439930638866
assert mactools.convert_to_int(mac2) == 281474976710655
assert mactools.convert_to_int(mac3) == 266081813921791
assert mactools.convert_to_int(mac4) == 38917505025
assert mactools.convert_to_int(mac5) == 256017920835632
assert mactools.convert_to_int(mac6) == 39863953827412

assert mactools.convert_to_bin(mac1) == '010011001100110000110100000100100001001000010010'
assert mactools.convert_to_bin(mac2) == '111111111111111111111111111111111111111111111111'
assert mactools.convert_to_bin(mac3) == '111100011111111111111111111111111111111111111111'
assert mactools.convert_to_bin(mac4) == '000000000000100100001111101010100000000000000001'
assert mactools.convert_to_bin(mac5) == '111010001101100011010001001110100100000000110000'
assert mactools.convert_to_bin(mac6) == '001001000100000110001100110011101010011001010100'

assert mactools.incr_mac(mac1) == '4c:cc:34:12:12:13'
assert mactools.incr_mac(mac3) == 'f2:00:00:00:00:00'
assert mactools.incr_mac(mac4) == '00:09:0f:aa:00:02'
assert mactools.incr_mac(mac5) == 'e8:d8:d1:3a:40:31'
assert mactools.incr_mac(mac6) == '24:41:8c:ce:a6:55'

assert mactools.decr_mac(mac1) == '4c:cc:34:12:12:11'
assert mactools.decr_mac(mac2) == 'ff:ff:ff:ff:ff:fe'
assert mactools.decr_mac(mac3) == 'f1:ff:ff:ff:ff:fe'
assert mactools.decr_mac(mac4) == '00:09:0f:aa:00:00'
assert mactools.decr_mac(mac5) == 'e8:d8:d1:3a:40:2f'
assert mactools.decr_mac(mac6) == '24:41:8c:ce:a6:53'

assert 'Motorola' in mactools.find_oui_org(mac1)
assert 'Could not find Organization' in mactools.find_oui_org(mac2)
assert 'Could not find Organization' in mactools.find_oui_org(mac3)
assert 'Fortinet' in mactools.find_oui_org(mac4)
assert 'HP Inc' in mactools.find_oui_org(mac5)
assert 'Intel Corporate' in mactools.find_oui_org(mac6)

assert mactools.get_oui(mac1) in mactools.find_org_ouis('Motorola')
assert mactools.get_oui(mac4) in mactools.find_org_ouis('Fortinet')
assert mactools.get_oui(mac5) in mactools.find_org_ouis('HP')
assert mactools.get_oui(mac6) in mactools.find_org_ouis('Intel')

# test ideas:
# - [x] test is_unicast
# - [x] test is_multicast
# - [x] test is_universal
# - [x] test is_local
# - [x] test is_oui
# - [x] test is_mac
# - [x] test find_oui_org
# - [x] test find_org_oui
# - [x] test convert_to_str/hex/int/bin
# - [x] test incr_mac
# - [x] test decr_mac
# - [ ] support convert_to_str/hex/int/bin input types other than str

print('All tests passed if you are reading this.')

