#!/usr/bin/env python3
#!python3
'''
Takes a CSV file and creates separate CSV files
filtered by vender and model of devices
'''
__version__ = '0.0.0'

import argparse
import pathlib
import re

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
f = args.filename

print(f'Input filename: `{f}`')
print(f'Input file stem: `{f.stem}`')
print(f'Input file suffix: `{f.suffix}`')

with open(f) as io:
    hdr = [io.readline()]
    t = io.readlines()

# Make backup of original file
print(f'Generating `{f.stem}-all{f.suffix}`')
pathlib.Path(f'{f.stem}-all{f.suffix}').write_text(
    pathlib.Path(f).read_text()
    )

# By vendor
print(f'Generating `{f.stem}-juniper{f.suffix}`')
print(f'Generating `{f.stem}-aruba{f.suffix}`')
pathlib.Path(f'{f.stem}-juniper{f.suffix}').write_text(''.join(
    hdr + [x for x in t if re.search('^[^,]*(?:345|1500)[^,]*,', x)]
    ))
pathlib.Path(f'{f.stem}-aruba{f.suffix}').write_text(''.join(
    hdr + [x for x in t if re.search('^[^,]*2930[^,]*,', x)]
    ))

# By model
print(f'Generating `{f.stem}-srx1500{f.suffix}`')
print(f'Generating `{f.stem}-srx345{f.suffix}`')
print(f'Generating `{f.stem}-2930f{f.suffix}`')
pathlib.Path(f'{f.stem}-srx1500{f.suffix}').write_text(''.join(
    hdr + [x for x in t if re.search('^[^,]*1500[^,]*,', x)]
    ))
pathlib.Path(f'{f.stem}-srx345{f.suffix}').write_text(''.join(
    hdr + [x for x in t if re.search('^[^,]*345[^,]*,', x)]
    ))
pathlib.Path(f'{f.stem}-2930f{f.suffix}').write_text(''.join(
    hdr + [x for x in t if re.search('^[^,]*2930[^,]*,', x)]
    #hdr + re.findall('^[^,]*2930[^,]*,.*', ''.join(t), re.MULTILINE)
    ))

