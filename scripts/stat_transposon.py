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


def read_fasta(file):

    '''Read fasta file'''
    if file.endswith(".gz"):
        fp = gzip.open(file)
    else:
        fp = open(file)

    seq = ""
    for line in fp:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if line.startswith(">"):
            if seq:
                yield seq.split("\n", 1)
            seq = "%s\n" % line.strip(">").split()[0]
            continue
        seq += line
    if seq:
        yield seq.split("\n", 1)
    fp.close()


def read_tsv(file):

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        yield line.split("\t")


def stat_transposon(gff, fasta, sample=""):

    tedict = OrderedDict([
        ("MITE", []),
        ("LTR", []),
        ("SINE", []),
        ("TER", []),
        ("HELITRON", []),
        ("Total", []),
    ])

    genome_length = 0
    for seqid, seq in read_fasta(fasta):
        genome_length += len(seq)
        if not sample:
            sample = seqid

    for i in read_tsv(gff):
        type, start, end = i[2], int(i[3]), int(i[4])
        if start >= end:
            start, end =  end, start
        length = end-start+1
        type = type.split("/")[0]
        tedict["Total"].append(length)
        if type in tedict:
            tedict[type].append(length)

    print("#sample\tType\tNumber\tAverage length(bp)\tLength(bp)\tGenome size(kb)\t% genome")

    for k, v in tedict.items():
        if v:
            print("{0:}\t{1:}\t{2:,}\t{3:,.2f}\t{4:,}\t{5:,.2f}\t{6:.2f}".format(
                sample, k, len(v), sum(v)*1.0/len(v), sum(v), genome_length/1000.0, sum(v)*100.0/genome_length)
            )

    return 0


def add_args(parser):

    parser.add_argument("fasta", metavar='FILE', type=str,
        help='Input sequence file, format(fasta).')
    parser.add_argument("-g", "--gff", metavar='FILE', type=str, required=True,
        help="Input transposon prediction results, format(gff).")
    parser.add_argument("-n", "--sample", metavar='STR', type=str, default='',
        help="Input sample name, default=seqid.")
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
    stat_transposon.py: Statistics of transposon prediction results
attention:
    stat_transposon.py genome.fasta -gff RepeatMasker.gff3 >stat_te.tsv
    stat_transposon.py genome.fasta -gff RepeatMasker.gff3 -n sample >stat_te.tsv
version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_args(parser)
    args = parser.parse_args()
    stat_transposon(args.gff, args.fasta, args.sample)


if __name__ == "__main__":
    main()
