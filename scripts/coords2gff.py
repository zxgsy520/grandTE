#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import argparse

LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def read_coords(file):

    LOG.info("reading message from %r" % file)

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("=") or line.startswith("[S1]"):
            continue
        line = line.replace("|", "")
        line = line.split()
        if len(line) < 10:
            continue

        yield line


def coords2gff(file, source="Mite_Hunter", type="MITE"):

    r = {}

    idy = 0
    for line in read_coords(file):
        if (line[0] == 0) and (line[1] != line[7]):
            continue
        idy = float(line[6])
        
        if line[9] not in r:
            r[line[9]] = [line[2], line[3], idy, line[10]]
            continue
        if idy >= r[line[9]][2]:
            r[line[9]] = [line[2], line[3], idy, line[10]]
    for i in r:
        start, end = int(r[i][0]), int(r[i][1])
        strand = "+"
        if start >= end:
            strand = "-"
            start, end = end, start

        print("{0}\t{1}\t{2}\t{3:}\t{4}\t{5:.2f}\t{6}\t.\tID={7}".format(
            r[i][3], source, type, start, end, r[i][2], strand, i)
        )

    return 0


def add_hlep_args(parser):

    parser.add_argument('coords', metavar='FILE', type=str,
        help='Input the nucmer comparison result file')
    parser.add_argument('-s', '--source', metavar='STR', type=str, default="Mite_Hunter",
        help='Software for input sequence source, default=Mite_Hunter.')
    parser.add_argument('-t', '--type', metavar='STR', type=str, default="MITE",
        help='Type of input sequence，default=MITE.')

    return parser


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
name:
    coords2gff.py: Get the gff file of the sequence by sequence comparison
attention:
    coords2gff.py seq.coords >seq.gff3
    coords2gff.py seq.coords --source Mite_Hunter --type MITE >seq.gff3
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    coords2gff(args.coords, args.source, args.type)


if __name__ == "__main__":

    main()
