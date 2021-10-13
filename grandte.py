#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from grandte.parser import *
from grandte.grand_mite import mite
from grandte.grand_ltr import ltr
from grandte.grand_sine import sine
from grandte.grand_tir import tir
from grandte.grand_helitron import helitron
from grandte.grand_repeat import repeat
from grandte.grand_all import grand_all
from grandte.grand_multi import grand_multi, add_grand_multi_args

from grandte import __version__, __email__, __author__


def add_grandte_parser(parser):

    subparsers = parser.add_subparsers(
        title='command',
        dest='commands')
    subparsers.required = True

    mite_parser = subparsers.add_parser("mite", help="Prediction MITE transposons")
    mite_parser = add_mite_args(mite_parser)
    mite_parser.set_defaults(func=mite)

    ltr_parser = subparsers.add_parser('ltr', help="Prediction LTR transposons")
    ltr_parser = add_ltr_args(ltr_parser)
    ltr_parser.set_defaults(func=ltr)
    
    sine_parser = subparsers.add_parser('sine', help="Prediction SINE transposons")
    sine_parser = add_sine_args(sine_parser)
    sine_parser.set_defaults(func=sine)

    tir_parser = subparsers.add_parser('tir', help="Prediction TIR transposons")
    tir_parser = add_tir_args(tir_parser)
    tir_parser.set_defaults(func=tir)
    
    helitron_parser = subparsers.add_parser('helitron', help="Prediction helitron transposons")
    helitron_parser = add_helitron_args(helitron_parser)
    helitron_parser.set_defaults(func=helitron)

    repeat_parser = subparsers.add_parser('repeat', help="Prediction repeat transposons")
    repeat_parser = add_repeat_args(repeat_parser)
    repeat_parser.set_defaults(func=repeat)

    grand_all_parser = subparsers.add_parser("all", help="all steps")
    grand_all_parser = add_all_args(grand_all_parser)
    grand_all_parser.set_defaults(func=grand_all)

    grand_multi_parser = subparsers.add_parser("multi", help="Multi-sample analysis of genes")
    grand_multi_parser = add_grand_multi_args(grand_multi_parser)
    grand_multi_parser.set_defaults(func=grand_multi)
    
    return parser


def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Next-generation sequencing data quality control.

version: %s
contact:  %s <%s>\
        """ % (__version__, " ".join(__author__), __email__))

    parser = add_grandte_parser(parser)
    args = parser.parse_args()

    args.func(args)

    return parser.parse_args()


if __name__ == "__main__":
    main()
