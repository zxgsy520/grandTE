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


def scn2gff(file, source="LTR_retriever", type="LTR"):

    locus = type
    n = 0
    for line in read_tsv(file):
        n += 1
        score = float(line[9])*100
        if line[-2]!="unknown":
            type = "%s/%s" % (type, line[-2])
        print("{seqid}\t{source}\t{type}\t{start}\t{end}\t{score:.2f}\t{strand}\t.\tID={locus_tag}".format(
                seqid=line[11], source=source, type=type, start=line[0], end=line[1],
                score=score, strand=line[12], locus_tag="%s_%05d" % (locus, n)
            )
        )
    return 0


def add_hlep_args(parser):

    parser.add_argument('input', metavar='FILE', type=str,
        help='Input LTR_retriever prediction result file')

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
    scn2gff.py: Convert LTR_retriever prediction result file to gff file
attention:
    scn2gff.py retriever.all.scn >retriever.gff
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    scn2gff(args.input)


if __name__ == "__main__":

    main()
