#!/usr/bin/env python3
"""Create a json file with the supported devices and required info."""

__version__ = '0.0.1'
__date__ = '2023-06-22'
__author__ = 'Todd Wintermute'

import json
import pathlib

json_file = 'device_models.json'
json_file = pathlib.Path(json_file)

models_dict = {
    'srx345': {'vendor': 'juniper', 'protocol': 'ftp', 'incr_mac': 1},
    'srx1500': {'vendor': 'juniper', 'protocol': 'ftp', 'incr_mac': None},
    'acx7024': {'vendor': 'juniper', 'protocol': 'ftp', 'incr_mac': 0x3ff},
    '2930f': {'vendor': 'aruba', 'protocol': 'tftp', 'incr_mac': None},
    'ex2300': {'vendor': 'juniper', 'protocol': 'ftp', 'incr_mac': None},
    'ex4100': {'vendor': 'juniper', 'protocol': 'ftp', 'incr_mac': None},
    }

with open(json_file, 'w') as f:
    json.dump(models_dict, f, indent=1)
