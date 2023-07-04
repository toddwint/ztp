#!/usr/bin/env python3
"""
My version of a Makefile written in Python.
This script converts a file from one format to another.
Pandoc is required plus texlive and texlive-latex-extra
"""
__version__ = '0.0.1'
__date__ = '2023-07-02'
__author__ = 'Todd Wintermute'

import argparse
import pathlib
import subprocess

input_files = list(pathlib.Path('../markdown/').glob('*.md'))
output_folder = pathlib.Path('../output') 
move_folder = pathlib.Path('../../../') #.resolve()
labels = [
    'all', 'html', 'pdf', 'docx', 'rtf', 'epub', 'clean', 'move', 'cleanall'
    ]

# Create command line arguments
parser = argparse.ArgumentParser(
    description='A python makefile-like utility to convert markdown \
documents to various formats using pandoc.',
    epilog='Have a nice day.',
    )
parser.add_argument(
    '-v', '--version',
    help='show the version number and exit',
    action='version',
    version= f'Version: %(prog)s  {__version__}  ({__date__})',
    )
parser.add_argument(
    'label',
    nargs='?',
    type=str,
    metavar='label',
    choices=labels,
    default='all',
    help=f'The label to execute. Default is "all". Choices are: {labels}.',
    )
args = parser.parse_args()

def all():
    html()
    pdf()
    #docx() # Not needed for this project
    #rtf() # Not needed for this project
    #epub() # Not needed for this project

def html():
    convert('.html')

def pdf():
    convert('.pdf')

def docx():
    convert('.docx')

def rtf():
    convert('.rtf')

def epub():
    convert('.epub')

def convert(ext):
    output_files = [output_folder / f'{i.stem}{ext}' for i in input_files]
    for infile, outfile in zip(input_files, output_files):
        pandoc_cmd(infile, outfile)

def pandoc_cmd(infile, outfile):
    fmap = {'infile': infile, 'outfile': outfile}
    command_str = 'pandoc -d config.yaml {infile} -o {outfile}'
    command = [x.format_map(fmap) for x in command_str.split()]
    ret = subprocess.run(
        command, capture_output=True, universal_newlines=True
        )
    print(' '.join(ret.args))
    if ret.returncode:
        print(ret.stderr)
    if ret.stdout:
        print(ret.stdout)

def clean():
    output_files = sorted(output_folder.glob('*'))
    for file in output_files:
        file.unlink()
        print(f'`{file}` deleted')

def move():
    output_files = sorted(output_folder.glob('*'))
    for file in output_files:
        newloc = move_folder / file.name
        print(f'`{file}` moved to `{newloc}`')
        file.replace(newloc)
    # copy source files too
    for file in input_files:
        newloc = move_folder / file.name
        print(f'`{file}` copied to `{newloc}`')
        newloc.write_text(file.read_text())

def cleanall():
    clean()
    # add any extra commands

if __name__ == '__main__':
    vars()[args.label]()
