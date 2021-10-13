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


def fa2maskerdb(files, types=""):

    for file in files:
        for seqid, seq in read_fasta(file):
            seqlen = len(seq)
            if types:
                seqid = "%s:LEN-%s#%s" % (seqid, seqlen, types)
            else:
                keys, values = seqid.split("_", 1)
                seqid = "%s:LEN-%s#%s" % (seqid, seqlen, keys)
            print(">%s\n%s" % (seqid, seq))
    return 0


def add_hlep_args(parser):

    parser.add_argument('fasta', nargs='+', metavar='FILE', type=str,
        help='Input sequence file, format(fasta).')
    parser.add_argument('--types', metavar='STR', type=str,
        choices=['', 'MITE', 'LTR', "SINE", "TER", "HELITRON"], default='',
        help='Input the transposon type.')

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
    fa2maskerdb.py: Build the RepeatMasker database
attention:
    fa2maskerdb.py *.TE.fa >te.lib
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    fa2maskerdb(args.fasta, args.types)


if __name__ == "__main__":

    main()
