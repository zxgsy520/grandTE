#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, get_version
from dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_tir_args


LOG = logging.getLogger(__name__)

LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_tirvish_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["tirvish"] = {
        "version": get_version(SOFTWARE_VERSION["tirvish"]),
        "option": "default"
    }
    tirvish_task = Task(
        id="tirvish",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={reasonaTE}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
gt suffixerator -db {prefix}.fasta -indexname {prefix}.index -tis -suf -lcp -des -ssp -sds -dna -mirrored
gt tirvish -index {prefix}.index > {prefix}.tirvish.gff3
{script}/get_gff2fa.py {prefix}.tirvish.gff3 -g {prefix}.fasta -tp repeat_region >{prefix}.tirvish.fasta
cp {prefix}.tirvish.gff3 {prefix}.tirvish.fasta {out_dir}
rm {prefix}.index.*
""".format(reasonaTE=REASONATE_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return tirvish_task, option, os.path.join(work_dir, "%s.tirvish.fasta" % prefix)


def run_tir(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "tirvish": "01_tirvish",
    }
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))

    dag = DAG("grand_ltr")
    tirvish_task, option, tirvish = create_tirvish_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["tirvish"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(tirvish_task)

    do_dag(dag, concurrent, refresh)

    return options, tirvish


def tir(args):

    options = run_tir(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_tir.json"), "w") as fh:
         json.dump(options, fh, indent=2)


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""


version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_tir_args(parser)
    args = parser.parse_args()
    tir(args)


if __name__ == "__main__":
    main()
