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


def read_tsv(file, sep=None):

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        yield line.split(sep)


def read_gff(file):

    r = []

    for line in read_tsv(file, "\t"):

        r.append(line)

    return r


def read_mustv2(file, source="MUSTv2", type="MITE"):

    r = []

    for line in read_tsv(file, "\t"):
        idy = "%.2f" % (float(line[12])*100.0)
        miteid = "ID=%s;Cluster=%s" % (line[1], line[2])
        line = [line[0], source, type, line[3], line[4], idy, line[5], ".", miteid]

        r.append(line)

    return r


def merge_mite(gffs, tsvs, locus="mite"):

    r = []

    for file in gffs:
        r += read_gff(file)
    if tsvs:
        for file in tsvs:
            r += read_mustv2(file)
    else:
        pass

    n = 0
    old_start = 0
    old_end = 0
    old_source = ""
    print("##gff-version 3")
    for record in sorted(r, key=lambda d: (d[0], int(d[3]))):
        if int(record[4])>=old_start and int(record[4])<=old_end and record[1]!=old_source:
            continue
        n += 1
        keks, parent = record[8].split("=", 1)
        print("{seqid}\t{source}\t{type}\t{start}\t{end}\t{score}\t{strand}\t{phase}\tID={locus_tag};Parent=={parent}".format(
                seqid=record[0], source=record[1], type=record[2], start=record[3], end=record[4],
                score=record[5], strand=record[6], phase=record[7], locus_tag="%s_%05d" % (locus, n), parent=parent
                ))
        old_start = int(record[3])
        old_end = int(record[4])
        old_source = record[1]
    return 0


def add_hlep_args(parser):

    parser.add_argument("-g", "--gffs", nargs="+", metavar="FILE", type=str,
        help='Input gff file')
    parser.add_argument("-ts", "--tsvs", nargs="+", metavar="FILE", type=str,
        help='Input tsv file.')
    parser.add_argument("-l", "--locus", metavar="STR", type=str, default="MITE",
        help="Input the locus_tag of the mite, default=MITE.")

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
    merge_mite.py: Merge MITE's forecast results
attention:
    merge_mite.py -g mitetracker.gff3 mite_hunter.gff3 -ts miteFinderII.tsv mustv2.tsv
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    merge_mite(args.gffs, args.tsvs, args.locus)


if __name__ == "__main__":

    main()
