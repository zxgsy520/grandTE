#!/usr/bin/env python
#coding:utf-8

import os
import re
import sys
import logging
import argparse


LOG = logging.getLogger(__name__)

__version__ = "1.1.1"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


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
            line = line.decode("utf-8")
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


def read_tsv(file, sep=None):

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        yield line.split(sep)



def read_masked_gff(file, mask_all=None):

    data = {}
    for line in read_tsv(file, "\t"):
        if not mask_all:
            if line[2] in ["Low_complexity", "Simple_repeat", "Satellite"]:
                continue
        if line[0] not in data:
            data[line[0]] = []
        start, end = int(line[3]), int(line[4])
        if start >= end:
            start, end = end, start

        data[line[0]].append([start, end])

    return data


def mask_seq(seq, masks, model="softmask"):

    r = seq
    for start, end in sorted(masks, key=lambda x: x[0]):
        if model == "softmask":
            r[start-1:end].lower()
            #r[start-1:end] = r[start-1:end].lower()
        elif model == "hardmaskX":
            r[start-1:end].replace("A","X").replace("T","X").replace("C","X").replace("G","X")
            #r[start-1:end] = r[start-1:end].replace("A","X").replace("T","X").replace("C","X").replace("G","X")
        else:
            r[start-1:end].replace("A","N").replace("T","N").replace("C","N").replace("G","N")
            #r[start-1:end] = r[start-1:end].replace("A","N").replace("T","N").replace("C","N").replace("G","N")

    return r


def format_seq(seq, length=100):

    r = re.findall('.{'+str(length)+'}', seq)
    r.append(seq[(len(r)*length):])

    return "\n".join(r)


def gff2masked(file, genome, mask_all=None, model="softmask"):

    data = read_masked_gff(file)

    for seqid, seq in read_fasta(genome):
        seq = seq.upper()
        if seqid not in data:
            print(">%s\n%s" % (seqid, seq))
            continue
        seq = mask_seq(seq, data[seqid], model)
        print(">%s\n%s" % (seqid, format_seq(seq)))

    return 0


def add_hlep_args(parser):

    parser.add_argument("gff", metavar="FILE", type=str,
        help="Input gff file for repeated predictions,(repeat.gff3)")
    parser.add_argument("-g", "--genome", metavar="FILE", type=str, required=True,
        help="Input genome file, (genome.fasta)")
    parser.add_argument("--mask_all", action="store_true",
        help="Masked all sequences.")
    parser.add_argument("-m", "--model", metavar="STR", type=str, default="hardmaskN",
        choices=["softmask", "hardmaskN", "hardmaskX"],
        help="""Choose a masking model,
             choices=[softmask, hardmaskN, hardmaskX]
             default=hardmaskN""")

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
    gff2masked.py: Genome masking based on duplicate annotation results.
attention:
    gff2masked.py repeat.gff3 -g genome.fasta >masked.fasta

    gff2masked.py repeat.gff3 -g genome.fasta --mask_all >masked.fasta
    #加入--mask_all，则对GFF文件中的所有重复序列进行屏蔽。
    #默认设置：不对Low_complexity、Simple_repeat、Satellite类型的重复序列进行屏蔽,
    #因为这种类型的重复序列长度较短，出现在基因区域的可能性较高;
    #对Unknown和Other类型的重复序列进行软屏蔽；对其它类型的转座子序列进行硬屏蔽。

    gff2masked.py repeat.gff3 -g genome.fasta --mask_all -m hardmaskX >masked.fasta
    #设置重复序列屏蔽模型有三个值可以选择：
    #softmask(将原本需要硬隐蔽的重复序列字符由大写字母换成小写字母)、
    #hardmaskX(将原本需要硬隐蔽的复序列字符替换成X)和hardmaskN(将原本需要硬隐蔽的重复序列字符替换成N)。

version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    gff2masked(args.gff, args.genome, args.mask_all, args.model)


if __name__ == "__main__":

    main()
