#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, get_version
from dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_helitron_args


LOG = logging.getLogger(__name__)

LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_helitronscanner_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["helitronscanner"] = {
        "version": get_version(SOFTWARE_VERSION["helitronscanner"]),
        "option": "default"
    }

    helitronscanner_task = Task(
        id="helitronscanner",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={reasonaTE}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
helitronscanner scanHead -g {prefix}.fasta -bs 0 -o {prefix}.scanHead.txt
helitronscanner scanTail -g {prefix}.fasta -bs 0 -o {prefix}.scanTail.txt
helitronscanner pairends -hs {prefix}.scanHead.txt -ts {prefix}.scanTail.txt -o {prefix}.helitronscanner.tsv
{script}/helitron2gff.py {prefix}.helitronscanner.tsv > {prefix}.helitron.gff
{script}/get_gff2fa.py {prefix}.helitron.gff -g {prefix}.fasta -tp all >{prefix}.helitron.fasta
cp {prefix}.helitronscanner.tsv {prefix}.helitron.gff {prefix}.helitron.fasta {out_dir}
""".format(reasonaTE=REASONATE_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return helitronscanner_task, option, os.path.join(work_dir, "%s.helitron.fasta" % prefix)


def run_helitron(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "helitron": "01_helitronscanner",
    }
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))
   
    dag = DAG("grand_helitron")
 
    helitronscanner_task, option, helitron = create_helitronscanner_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["helitron"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(helitronscanner_task)

    do_dag(dag, concurrent, refresh)

    return options, helitron


def helitron(args):

    run_helitron(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_helitron.json"), "w") as fh:
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

    parser = add_helitron_args(parser)
    args = parser.parse_args()
    helitron(args)


if __name__ == "__main__":
    main()
