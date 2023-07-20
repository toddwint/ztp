#!/usr/bin/env python3
"""
Print a CSV file formatted as a table in the console.
"""

__version__ = '0.0.2'
__author__ = 'Todd Wintermute'
__date__ = '2023-07-19'

import argparse
import csv
import pathlib
import re
import sys

def parse_arguments():
    """Takes arguments from the command line. Returns a parser object."""
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
    return parser

def csvfile_to_list(filename):
    """Takes a CSV as a pathlib object. Returns it as a list."""
    if not filename.exists():
        print(f"Could not open file: `{filename}`")
        sys.exit()
    # Don't forget newline='' or '\n' chars in a cell will be missed
    with filename.open(newline='') as f:
        csvtext = f.readlines()
    return list(csv.reader(csvtext))

def sanitize_for_newlines(csvlist):
    """If newlines are found within a cell, we're taking the item 
    on the last line and prefixing it with the characters "..." to show 
    additional information is present in the cell.
    """
    csvlist = [
        [re.sub('(?:.*\n)+', '...', item) for item in row] 
        for row in csvlist
    ]
    return csvlist

def csvlist_pretty_print(csvlist):
    """Takes a CSV parsed as a list. Returns the console formatted text."""
    columns = len(max(csvlist, key=len))
    column_sizes = [len(max(column, key=len)) for column in zip(*csvlist)]
    # Make last column size fixed to hdr size so text wraps instead of grow
    column_sizes[-1] = len(csvlist[0][-1])
    # Find the max length of a column, if multiple rows in a cell
    # Not very easy to do in a console window. Not using this.
    #column_sizes = [
    #    len(max([line for cell in [line.split('\n') for line in column]
    #        for line in cell], key=len))
    #    for column in zip(*csvlist)
    #    ]
    formatted_output = '\n'.join(
        ['  '.join(
            [
            f"{item:<{size}}" for size, item in zip(column_sizes, row)
            ]
                ) for row in csvlist
        ]
    )
    return formatted_output

def main():
    """Calls the main function to run this program directly."""
    parser = parse_arguments()
    args = parser.parse_args()
    csv_list = csvfile_to_list(args.filename)
    csv_list = sanitize_for_newlines(csv_list)
    print(csvlist_pretty_print(csv_list))

if __name__ == '__main__':
    main()
