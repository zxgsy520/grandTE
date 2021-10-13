#!/usr/bin/env python
#coding:utf-8

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


def split_attr(attributes):

    attr = attributes.split()
    start = int(attr[-2])
    end = int(attr[-1])
    if start >= end:
        start, end = end, start

    matchlen = end-start+1
    attr = attr[-3].strip('"').split(":")
    types, values = attr[-2].split("_", 1)
    key, seqlen = attr[-1].split("-", 1)
    seqid = ":".join(attr[1::])

    return seqid, types, int(seqlen), matchlen


def filter_masker(file, mperc=50, minlen=80):

    name = file.split("/")[-1]
    name  = ".".join(name.split(".")[0:-1])
    fo = open("%s.gff3" % name, "w")

    rn = {}
    for line in read_tsv(file, "\t"):
        seqid, types, seqlen, matchlen = split_attr(line[-1])
        if (matchlen*100.0/seqlen) < mperc:
            continue
        if seqlen < minlen:
            continue
        if types not in rn:
            rn[types] = 0
        rn[types] += 1
        line[2] = types
        print("\t".join(line))
        line[-1] = "ID=%s_%05d;note=%s" % (types, rn[types], seqid)
        fo.write("%s\n" % "\t".join(line))

    fo.close()


def add_hlep_args(parser):

    parser.add_argument('gff', metavar='FILE', type=str,
        help='Input the gff file annotated by RepeatMasker')
    parser.add_argument('-mp','--mperc', metavar='INT', type=int, default=50,
        help='Keep match length percentage, default=50.')
    parser.add_argument('-l','--minlen', metavar='INT', type=int, default=80,
        help='Keep the minimum sequence length, default=80.')

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
    filter_masker.py: Filter RepeatMasker annotation results
attention:
    filter_masker.py RepeatMasker.gff > RepeatMasker_new.gff
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    filter_masker(args.gff, args.mperc, args.minlen)


if __name__ == "__main__":

    main()
