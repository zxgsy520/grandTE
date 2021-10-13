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


def read_gff(file):

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        yield line.split("\t")


def read_fasta(file):

    '''Read fasta file'''
    if file.endswith(".gz"):
        fp = gzip.open(file)
    elif file.endswith(".fasta") or file.endswith(".fa"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = []
    for line in fp:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if line.startswith(">"):
            line = line.strip(">")
            if len(seq) == 2:
                yield seq
            seq = []
            seq.append(line.split()[0])
            continue
        if len(seq) == 2:
            seq[1] += line
        else:
            seq.append(line)

    if len(seq) == 2:
        yield seq
    fp.close()


def complement(seq):

    cdict = {"A": "T",
        "T": "A",
        "G": "C",
        "C": "G"
    }

    seq = list(seq.upper())
    nseq = ""
    for i in seq:
        nseq += cdict[i]

    return nseq


def reverse_complement(seq):

    seq = seq[::-1]

    return complement(seq)


def split_attr(attributes):

    r = {}

    for content in attributes.split(';'):
        if not content:
            continue
        if '=' not in content:
            print('%r is not a good formated attribute: no tag!')
            continue
        tag, value = content.split('=', 1)
        r[tag] = value

    return r


def get_gff2fa(fasta, gff, types):

    data = {}

    for line in read_gff(gff):
        if (types != line[2]) and (types != "all"):
            continue
        if line[0] not in data:
            data[line[0]] = []

        attr = split_attr(line[8])
        data[line[0]].append([attr["ID"], int(line[3]), int(line[4])])

    for seqid, seq in read_fasta(fasta):
        if seqid not in data:
            continue
        for rnaid, start, end in data[seqid]:
            direct = "+"
            if start >= end:
                direct = "-"
                start, end = end, start
            nseq = seq[start-1:end]
            if direct == "-":
                nseq = reverse_complement(nseq)

            print(">%s desc=%s-%s\n%s" % (rnaid, start, end, nseq))

    return 0


def add_hlep_args(parser):

    parser.add_argument('gff', metavar='FILE', type=str,
        help='Input gff file')
    parser.add_argument('-g', '--genome', metavar='FILE', type=str, required=True,
        help='Input genome file.')
    parser.add_argument('-tp', '--types', choices=["CDS", "rRNA", "tRNA", "gene", "MITE", "SINE", "repeat_region", "all"], default="MITE",
        help='Input the type of extraction sequence,　default=MITE.')

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
    get_gff2fa.py: Extract the sequence of the specified type according to the gff problem
attention:
    get_gff2fa.py MITE.gff3 -s genome.fasta -t MITE >MITE.fasta
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    get_gff2fa(args.genome, args.gff, args.types)


if __name__ == "__main__":

    main()
