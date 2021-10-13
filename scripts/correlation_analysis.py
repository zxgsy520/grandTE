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
import scipy.stats as stats
from scipy.optimize import curve_fit
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


def read_transposon(file, model="length"):

    if model== "length":
        model = 4
    elif model== "number":
        model = 2
    else:
        model = -1

    r = {}
    for line in read_tsv(file):
        r[line[0]] = [int(float(line[model])), float(line[5])]

    telen = []
    glen = []
    for name, values in sorted(r.items(), key=lambda d:d[1][0]):
        telen.append(values[0])
        glen.append(values[1])

    return telen, glen


def linear_model(x, a, b):
    
    return a*x+b


def correlation_analysis(x, y):

    x = np.array(x)
    y = np.array(y)

    r, p = stats.pearsonr(x, y)
    p_fit, pcov = curve_fit(linear_model, x, y)
    a, b = p_fit.tolist()
    ny = a*x+b
    print("y=%.6f*x+%.6f" % (a, b))
    print("R value\tP value\n%.6f\t%.6f" % (r, p))

    return x, y, ny


def plot_correlation_analysis(telen, glen, plen):

    fig = plt.figure(figsize=(8, 5.5))
    ax = fig.add_subplot(111)

    plt.tick_params(labelsize=12)
    font = {'family': 'Times New Roman', 'weight': 'normal', 'color': '#212121', 'size': 14}
    ax.set_ylabel('Genome(kb)', font)
    ax.set_xlabel('Transposon length(bp)', font)
    ax.plot(telen, glen, "o", color='#FFA000', markersize=8)
    ax.plot(telen, plen, linestyle="-.", color='#212121', linewidth=0.5)
    ax.tick_params(axis='both', which='both', color='#212121', length=5, width=1.5)
    ax.spines['top'].set_visible(False)#去掉上边边框
    ax.spines['bottom'].set_linewidth(1.5)
    #ax.spines['bottom'].set_visible(False)#去掉下方边边框
    ax.spines['right'].set_visible(False)#去掉右边边框
    #ax.spines['left'].set_visible(False)#去掉左边边框
    ax.spines['left'].set_linewidth(1.5)

    #fig.tight_layout()
    plt.savefig('transposon_correlation_analysis.png', dpi=700)
    plt.savefig('transposon_correlation_analysis.pdf')
    return 0


def plot_transposon(telen, glen):

    fig = plt.figure(figsize=(8, 5.5))
    ax1 = fig.add_subplot(111)
    x = range(len(telen))

    #plt.grid(True, which='minor', axis='both', lw=1.5, color='#E5C700', alpha=0.3)
    #plt.grid(True, which='major', axis='both', lw=2, color='#E2BDD5', alpha=0.3)
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='black', alpha=.3)
    plt.grid(True, 'major', 'x', ls='--', lw=.5, c='black', alpha=.3)
    plt.grid(True, 'minor', 'x', ls='--', lw=.5, c='black', alpha=.3)
    ax1.spines['top'].set_visible(False)#去掉上边边框
    ax1.spines['bottom'].set_visible(False)#去掉下方边边框
    ax1.spines['right'].set_visible(False)#去掉右边边框
    ax1.spines['left'].set_visible(False)#去掉左边边框
    plt.tick_params(bottom=False, top=False, left=False, right=False, labelsize=12)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(''.format)) #X轴不显示刻度
    ax1.xaxis.set_minor_formatter(plt.FuncFormatter(''.format))

    ax1.tick_params(axis='both', which='both', color='#ffffff', length=0, width=2)
    font1 = {'family': 'Times New Roman', 'weight': 'normal', 'color': '#212121', 'size': 14}
    ax1.set_ylabel('Transposon length(bp)', font1)
    ax1.plot(x, telen, "o", color='#212121', markersize=8, label='Transposon length')
    ax1.plot(x, telen, "-.", color='#212121')
    

    font2 = {'family': 'Times New Roman', 'weight': 'normal', 'color': '#FFA000', 'size': 14}
    ax2 = ax1.twinx()
    
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='black', alpha=.3)
    plt.grid(True, 'major', 'x', ls='--', lw=.5, c='black', alpha=.3)
    plt.grid(True, 'minor', 'x', ls='--', lw=.5, c='black', alpha=.3)
    plt.tick_params(bottom=False, top=False, left=False, right=False, labelsize=12)
    ax2.set_ylabel('Genome(kb)', font2)
    ax2.plot(x, glen, "o", color='#FFA000', markersize=8, label='Genome')
    ax2.plot(x, glen, "-.", color='#FFA000')
    ax2.tick_params(axis='both', which='both', color='#ffffff', length=0, width=2)

    ax2.spines['top'].set_visible(False)#去掉上边边框
    ax2.spines['bottom'].set_visible(False)#去掉下方边边框
    ax2.spines['right'].set_visible(False)#去掉右边边框
    ax2.spines['left'].set_visible(False)#去掉左边边框

    
    fig.tight_layout()
    plt.savefig('genomic_transposon_length.png', dpi=700)
    plt.savefig('genomic_transposon_length.pdf')

    return 0


def add_args(parser):

    parser.add_argument("input", metavar='FILE', type=str,
        help='Input the statistical results of each sample transposon, stat_transposon.tsv.')
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
    correlation_analysis.py: Draw a picture of the transposon
attention:
    correlation_analysis.py *.stat_transposon.tsv
version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_args(parser)
    args = parser.parse_args()

    telen, glen = read_transposon(args.input, args.model)
    telen, glen, plen = correlation_analysis(telen, glen)
    plot_correlation_analysis(telen, glen, plen)
    #plot_transposon(telen, glen)


if __name__ == "__main__":
    main()
