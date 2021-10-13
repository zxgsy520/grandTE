#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import argparse

from collections import OrderedDict

LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def read_tsv(file):

    header = ""
    for line in open(file):
        line = line.strip()

        if not line:
            continue
        if line.startswith("#"):
            header = line.split("\t")
            continue
        yield header, line.split("\t")


def class_stat_transposon(files):

    r = OrderedDict()
    header = ""

    for file in files:
        for j, line in read_tsv(file):
            if line[1] not in r:
                r[line[1]] = []
            r[line[1]].append(line)
        header = j

    for i in r:
        fo = open("%s_transposon.tsv" % i, "w")
        fo.write("%s\n" % "\t".join(header))
        for j in r[i]:
            fo.write("%s\n" % "\t".join(j))
        fo.close()

    return 0


def add_args(parser):

    parser.add_argument("input",  nargs='+', metavar='FILE', type=str,
        help='Input the statistical results of each sample transposon, stat_transposon.tsv.')

    return parser


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
name:
    class_stat_transposon.py: Statistics of each sample data according to the type of transposon
attention:
    class_stat_transposon.py *.stat_transposon.tsv
version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_args(parser)
    args = parser.parse_args()
    class_stat_transposon(args.input)


if __name__ == "__main__":
    main()
