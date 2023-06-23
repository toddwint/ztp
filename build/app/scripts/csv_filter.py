#!/usr/bin/env python3
"""
Takes a CSV file and creates separate CSV files
filtered by vender and model of devices
"""

__version__ = '0.0.2'
__date__ = '2023-06-22'
__author__ = 'Todd Wintermute'

import argparse
import json
import pathlib
import re
import sys

device_models_json = 'device_models.json'

device_models_json = pathlib.Path(device_models_json)
if not device_models_json.exists():
    print(f'Could not find file `{device_models_json}`. Bye!')
    sys.exit()
device_models = json.loads(device_models_json.read_text())

parser = argparse.ArgumentParser(
    description=__doc__, 
    epilog='You got this!',
    )
parser.add_argument(
    '-v', '--version', 
    help='show the version number and exit', 
    action='version', 
    version=f'Version: {__version__}',
    )
parser.add_argument(
    'filename', 
    nargs='?',
    type=pathlib.Path,
    default='ztp.csv',
    help=f'name of CSV file (default=%(default)s)',
    )
args = parser.parse_args()
file = args.filename

print(f'Input filename: `{file}`')

with open(file) as f:
    hdr = [f.readline()]
    lines = f.readlines()

# Make backup of original file
print(f'Generating `{file.stem}-all{file.suffix}`')
pathlib.Path(f'{file.stem}-all{file.suffix}').write_text(
    pathlib.Path(file).read_text()
    )

# Make a list of vendors and models from device_models dict
vendors = set([value['vendor'] for key,value in device_models.items()])
models = set(device_models.keys())

# By vendor
for vendor in vendors:
    models_match = [
        key for key,value in device_models.items()
        if value['vendor'] == vendor
            ]
    r = re.compile(f"""^[^,]*(?:{'|'.join(models_match)})[^,]*,""")
    if any([r.search(x) for x in lines]):
        print(f'Generating `{file.stem}-{vendor}{file.suffix}`')
        output_file = pathlib.Path(f'{file.stem}-{vendor}{file.suffix}')
        output_text = ''.join(hdr + [x for x in lines if r.search(x)])
        output_file.write_text(output_text)

# By model
for model in models:
    r = re.compile(f"""^[^,]*{model}[^,]*,""")
    if any([r.search(x) for x in lines]):
        print(f'Generating `{file.stem}-{model}{file.suffix}`')
        output_file = pathlib.Path(f'{file.stem}-{model}{file.suffix}')
        output_text = ''.join(hdr + [x for x in lines if r.search(x)])
        output_file.write_text(output_text)

print('Done!')
