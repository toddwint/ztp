#!/usr/bin/env python3
"""
Print a CSV file formatted as a table in the console.
"""

__version__ = '0.0.1'
__author__ = 'Todd Wintermute'
__date__ = '2023-05-05'

import argparse
import csv
import pathlib
import sys

def parse_arguments():
    """Takes arguments from the command line. Returns a parse_args object."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='Enjoy!',
        )
    parser.add_argument(
        '-v', '--version',
        help='show the version number and exit',
        action='version',
        version=f'Version: %(prog)s  {__version__}  ({__date__})',
        )
    parser.add_argument(
        'filename',
        type=pathlib.Path,
        help=f'name of CSV file',
        )
    return parser.parse_args()


def csvfile_to_list(filename):
    """Takes a CSV as a pathlib object. Returns it as a list."""
    if not filename.exists():
        print(f"Could not open file: `{filename}`")
        sys.exit()
    csvtext = filename.read_text().splitlines()
    return list(csv.reader(csvtext))


def csvlist_pretty_print(csvlist):
    """Takes a CSV parsed as a list. Returns the console formatted text."""
    columns = len(max(csvlist, key=lambda x: len(x)))
    column_sizes = [
        len(max(csvlist, key=lambda x: len(x[column]))[column]) 
        for column in range(columns)
            ]
    formatted_output = '\n'.join(['  '.join(
        [f"{item:<{size}}" for size, item in zip(column_sizes, row)]
        ) for row in csvlist
        ])
    ## Similar to this code below
    #for row in csvlist:
    #    for size, item in zip(column_sizes, row):
    #        print(f"{item:<{size}}", end='  ')
    #    print()
    return formatted_output

def main():
    """Calls the main function to run this program directly."""
    args = parse_arguments()
    csv_list = csvfile_to_list(args.filename)
    print(csvlist_pretty_print(csv_list))
    
if __name__ == '__main__':
    main()
