#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import argparse
import matplotlib
matplotlib.use('Agg')

import numpy as np
from collections import OrderedDict
from matplotlib import pyplot as plt

LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def read_tsv(file):

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        line = line.replace(",", "")

        yield line.split("\t")


def deal_with(files, types="all", model="length"):

    r = {}
    if types=="all":
        types = ["MITE", "LTR", "SINE", "TER", "HELITRON"]

    if model== "length":
        model = 4
    elif model== "number":
        model = 2
    else:
        model = -1

    for file in files:
        for line in read_tsv(file):
            if line[0] not in r:
                r[line[0]] = [float(line[5]), []]
            if line[1] not in types:
                continue
            r[line[0]][1].append((line[1], float(line[model])))

    pr = OrderedDict()
    sample = []
    for name, values in sorted(r.items(), key=lambda d:d[1][0], reverse=True):
        sample.append(name.replace("_", " ").capitalize())
        for types, dv in values[1]:
            if types not in pr:
                pr[types] = []
            pr[types].append(dv)
    return sample, pr


def plot_transposon(files, types="all", model="length"):

    sample, pr = deal_with(files, types, model)
    if model == "length":
        yl = "Transposon length(pb)"
    elif model == "number":
        yl = "Transposon number"
    else:
        yl = "% transposon"
    #PCOLOR = ["#E6FA3C", "#E6AD67", "#FA2883", "#524CE6", "#6AFFE0"]
    #PCOLOR = ["#8975FA", "#3BA5F0", "#91FAD7", "#83E673", "#FFFA4D"]
    #PCOLOR = ["#FA2843", "#62F0A3", "#FA7D5A", "#5AEAE3", "#FF8619"]
    #PCOLOR = ["#0780cf", "#765005", "#fa6d1d", "#0e2c82", "#b6b51f"]
    PCOLOR = ["#015699", "#FAC00F", "#F3764A", "#5FC6C9", "#4F596D"]

    fig = plt.figure(figsize=[10,8.5])
    ax = fig.add_subplot(1,1,1,)   
 
    ax.spines['top'].set_visible(False)#去掉上边边框
    ax.spines['bottom'].set_visible(False)#去掉下方边边框
    ax.spines['right'].set_visible(False)#去掉右边边框
    ax.spines['left'].set_visible(False)#去掉左边边框
    ax.grid(True, 'major', 'y', ls='--', lw=.5, c='black', alpha=.3)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(''.format)) #X轴不显示刻度
    ax.xaxis.set_minor_formatter(plt.FuncFormatter(''.format))

    plt.tick_params(bottom=False, top=False, left=False, right=False, labelsize=12)
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.25)
    n = 0
    x = np.array(sample)

    for i in pr:
        y = np.array(pr[i])
        if n == 0:
            ax.bar(x, y, label=i, color=PCOLOR[n])
            h = y
        else:
            ax.bar(x, y, bottom=h, label=i, color=PCOLOR[n])
            h = h+y
        n += 1

    for a,b in zip(x, sample):
       ax.text(a, -2, b, ha='right', va='top', fontsize=12, rotation=45)

    plt.legend(loc="upper right", frameon=False)
    plt.ylabel(yl, fontsize=14)
    plt.savefig("%s_transposon.png" % types, dpi=500)
    plt.savefig("%s_transposon.pdf" % types)

    return 0


def add_args(parser):

    parser.add_argument("input",  nargs='+', metavar='FILE', type=str,
        help='Input the statistical results of each sample transposon, stat_transposon.tsv.')
    parser.add_argument('-t', '--types', choices=["MITE", "LTR", "SINE", "TER", "HELITRON", "all"], default="all",
        help='Set the type of transposon displayed, default=all.')
    parser.add_argument('-m', '--model', choices=["length", "number", "percentage"], default="length",
        help='Set the type of data displayed, default=length.')

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
    plot_transposon.py: Draw a picture of the transposon
attention:
    plot_transposon.py *.stat_transposon.tsv
version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_args(parser)
    args = parser.parse_args()

    plot_transposon(args.input, args.types, args.model)


if __name__ == "__main__":
    main()
