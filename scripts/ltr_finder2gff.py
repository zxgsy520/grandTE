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


def read_ltr_finder(file):

    r = []
    for line in open(file):
        line = line.strip()

        if line.startswith("["):
            r.append(line.split()[1])
        elif line.startswith("Location"):
            line = line.split()
            r += [line[2], line[4], line[-1].split(":")[1]]
        elif line.startswith("Score"):
            line = line.split(":")
            score = float(line[-1].strip("]"))*100
            r.append(score)
            yield r
            r = []
        else:
            continue


def ltr_finder2gff(file, source="ltr_finder", type="LTR"):

    locus = type
    n = 0
    for seqid, start, end, strand, score in read_ltr_finder(file):
        n += 1
        print("{seqid}\t{source}\t{type}\t{start}\t{end}\t{score:.2f}\t{strand}\t.\tID={locus_tag}".format(
                seqid=seqid, source=source, type=type, start=start, end=end,
                score=score, strand=strand, locus_tag="%s_%05d" % (locus, n)
            )
        )
    return 0


def add_hlep_args(parser):

    parser.add_argument('input', metavar='FILE', type=str,
        help='Input ltr_finder prediction result file')

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
    ltr_finder2gff.py: Convert ltr_finder prediction result file to gff file
attention:
    ltr_finder2gff.py ltr_finder.tsv >ltr_finder.gff
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    ltr_finder2gff(args.input)


if __name__ == "__main__":

    main()
