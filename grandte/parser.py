#!/usr/bin/env python
# -*- coding: utf-8 -*-

from grandte.config import *

__all__ = ["add_trf_args", "add_mite_args", "add_ltr_args", "add_sine_args", "add_tir_args", "add_helitron_args", "add_repeat_args", "add_all_args"]


def add_workflow_args(parser):
    """
    add workflow arguments to parser
    :param parser: argparse object
    :return: parser
    """

    workflow_group = parser.add_argument_group(title="Workflow arguments", )
    workflow_group.add_argument("--concurrent", metavar="INT", type=int, default=10,
        help="Maximum number of jobs concurrent  (default: 10).")
    workflow_group.add_argument("--refresh", metavar="INT", type=int, default=30,
        help="Refresh time of log in seconds  (default: 30).")
    workflow_group.add_argument("--job_type", choices=["sge", "local"], default="local",
        help="Jobs run on [sge, local]  (default: local).")
    workflow_group.add_argument("--work_dir", metavar="DIR", type=str, default=".",
        help="Work directory (default: current directory).")
    workflow_group.add_argument("--out_dir", metavar="DIR", type=str, default=".",
        help="Output directory (default: current directory).")

    return parser


def add_trf_args(parser):

    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="mite",
        help="Input the name of the analysis sample.")
    parser.add_argument("-g", "--genome", metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("-gs", "--genomes", nargs='+', metavar="FILE", type=str, required=True,
        help="Inter the split genome.")
    parser = add_workflow_args(parser)

    return parser


def add_mite_args(parser):

    parser.add_argument("-g", "--genome", nargs='+', metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="mite",
        help="Input the name of the analysis sample.")
    parser.add_argument("-t", "--thread", metavar="INT", type=int, default=4,
        help="Maximum number of CPU cores to use (default=4)")
    parser = add_workflow_args(parser)

    return parser


def add_ltr_args(parser):

    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="mite",
        help="Input the name of the analysis sample.")
    parser.add_argument("-g", "--genome", metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("-gs", "--genomes", nargs='+', metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("--kingdom", metavar="STR", type=str, choices=["fungi", "animal", "plant"], default="fungi",
        help="Kingdom of the sample (default: fungi)")
    parser.add_argument("--thread", type=int, default=4,
        help="Maximum number of CPU cores to use (default=4)")
    parser = add_workflow_args(parser)

    return parser


def add_sine_args(parser):

    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="mite",
        help="Input the name of the analysis sample.")
    parser.add_argument("-g", "--genome", metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("-gs", "--genomes", nargs='+', metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("--thread", type=int, default=4,
        help="Maximum number of CPU cores to use (default=4)")
    parser = add_workflow_args(parser)

    return parser


def add_tir_args(parser):

    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="mite",
        help="Input the name of the analysis sample.")
    parser.add_argument("-gs", "--genomes", nargs='+', metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("--thread", type=int, default=4,
        help="Maximum number of CPU cores to use (default=4)")
    parser = add_workflow_args(parser)

    return parser


def add_helitron_args(parser):

    parser = add_tir_args(parser)

    return parser


def add_repeat_args(parser):

    parser.add_argument("genome", metavar="FILE", type=str,
        help="Input genome file.")
    parser.add_argument("-gs", "--genome",  nargs='+', metavar="FILE", type=str, required=True,
        help="Input the split genome.")
    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="mite",
        help="Input the name of the analysis sample.")
    parser.add_argument("-l", "--libs", nargs='+', metavar="FILE", type=str, default="",
        help="Input prediction database.")
    parser.add_argument("-s", "--species", metavar="FILE", type=str, default="",
        help="Input species name.")
    parser.add_argument("-m", "--mode", choices=["fast", "general", "strict"], default="general",
        help="Choose the mode of operation, default=general.")
    parser.add_argument("--kingdom" , choices=["plant", "animal", "fungi"], default="fungi",
        help="Choose kingdom, default=fungi.")
    parser.add_argument("--thread", type=int, default=4,
        help="Maximum number of CPU cores to use (default=4)")
    parser = add_workflow_args(parser) 

    return parser


def add_all_args(parser):

    parser.add_argument("-g", "--genome", metavar="FILE", type=str, required=True,
        help="Input genome file.")
    parser.add_argument("-p", "--prefix", metavar="STR", type=str, default="TE",
        help="Input the name of the analysis sample.")
    parser.add_argument("--kingdom", metavar="STR", type=str, choices=["fungi", "animal", "plant"], default="fungi",
        help="Kingdom of the sample (default: fungi), choices=[fungi, animal, plant]")
    parser.add_argument("-s", "--species", metavar="FILE", type=str, default="",
        help="Input species name.")
    parser.add_argument("-m", "--mode", choices=["fast", "general", "strict"], default="general",
        help="Choose the mode of operation, default=general.")
    parser.add_argument("-t", "--thread", metavar="INT", type=int, default=4,
        help="Maximum number of CPU cores to use (default=4)")
    parser = add_workflow_args(parser)

    return parser
