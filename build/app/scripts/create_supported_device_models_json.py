#!/usr/bin/env python3
"""Create a json file with the supported devices and required info."""

__version__ = '0.0.1'
__date__ = '2023-06-27'
__author__ = 'Todd Wintermute'

import json
import pathlib

json_file = '../configs/supported_device_models.json'
json_file = pathlib.Path(json_file)

models_dict = {
    'srx345': {'vendor': 'juniper', 'incr_mac': 1},
    'srx1500': {'vendor': 'juniper', 'incr_mac': None},
    'acx7024': {'vendor': 'juniper', 'incr_mac': 0x3ff},
    '2930f': {'vendor': 'aruba', 'incr_mac': None},
    'ex2300': {'vendor': 'juniper', 'incr_mac': None},
    'ex4100': {'vendor': 'juniper', 'incr_mac': None},
    }

with open(json_file, 'w') as f:
    json.dump(models_dict, f, indent=1)
