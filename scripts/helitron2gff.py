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


def read_helitronscanner(file):

    r = []

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        if line.startswith(">"):
            line = line.strip(">")
            r.append(line.split()[0])
            continue
        r.append(line)
        yield r
        r = []


def sum_score(score):

    r = 0
    score = score.strip("[").split(";")[0]

    for i in score.split(":", 1):
        r += int(i)

    return r


def split_helitrons(helitrons):

    for line in helitrons.replace("][", ";").split("]"):

        line = line.strip()
        if not line:
            continue

        location, score = line.split(" ", 1)
        start, end = location.split(":", 1)
        score = sum_score(score)

        yield start, end, score


def helitron2gff(file, source="", type="", locus=""):

    n = 0
    for seqid, helitrons, in read_helitronscanner(file):
        for start, end, score in split_helitrons(helitrons):
            n += 1
            print("{seqid}\t{source}\t{type}\t{start}\t{end}\t{score}\t.\t.\tID={locus_tag}".format(
                    seqid=seqid, source=source, type=type, start=start, end=end,
                    score=score, locus_tag="%s_%05d" % (locus, n)
                )
            )

    return 0


def add_hlep_args(parser):

    parser.add_argument('input', metavar='FILE', type=str,
        help='Input the prediction result of helitronscanner')
    parser.add_argument('-s', '--source', metavar='STR', type=str, default="helitronscanner",
        help='Input prediction software，default=helitronscanner')
    parser.add_argument('-tp', '--type',metavar='STR', type=str, default="helitron",
        help='Input the type of prediction sequence,　default=helitron.')
    parser.add_argument('-l', '--locus',metavar='STR', type=str, default="HELITRON",
        help='Input the sequence prefix name,　default=HELITRON.')

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
    helitron2gff.py: Convert helitronscanner prediction results into gff files
attention:
    helitron2gff.py helitronscanner.tsv >helitronscanner.gff
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    helitron2gff(args.input, args.source, args.type, args.locus)


if __name__ == "__main__":

    main()
