#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, read_tsv
from dagflow import DAG, Task, do_dag

LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_grandTE_task(prefix, genome, job_type, work_dir, out_dir):

    task = Task(
        id="grandTE_%s" % prefix,
        work_dir=work_dir,
        type="local",
        option="-pe smp 1",
        script="""
{root}/grandte.py all \\
--prefix {prefix} --genome {genome} \\
--thread 1 --job_type {job_type} \\
--work_dir {work}/{prefix}  --out_dir {out}/{prefix}
""".format(root=ROOT,
            prefix=prefix,
            genome=genome,
            job_type=job_type,
            work=work_dir,
            out=out_dir
        )
    )

    return task


def class_te(tes, job_type, work_dir, out_dir):

    task = Task(
        id="class",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp 1",
        script="""
{script}/class_stat_transposon.py {tes}
cp *_transposon.tsv {out_dir}
{script}/plot_transposon.py {tes} 
mv all_transposon.png Length_all_transposon.png
mv all_transposon.pdf Length_all_transposon.pdf
{script}/plot_transposon.py {tes} --model number
mv all_transposon.png Number_all_transposon.png
mv all_transposon.pdf Number_all_transposon.pdf
cp *_all_transposon.png *_all_transposon.pdf {out_dir}
""".format(script=SCRIPTS,
            tes=tes,
            out_dir=out_dir
        )
    )

    return task


def run_grand_multi(genomes, work_dir, out_dir, concurrent, refresh, job_type="local"):

    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)
    genomes = check_path(genomes)

    dag = DAG("grand_multi")
    class_task = class_te(
        tes=os.path.join(out_dir, "*/06_repeat/*.stat_transposon.tsv"),
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir
    )
    dag.add_task(class_task)

    for line in read_tsv(genomes):
        genome = check_path(line[1])
        task = create_grandTE_task(
            prefix=line[0],
            genome=genome,
            job_type=job_type,
            work_dir=work_dir,
            out_dir=out_dir
        )
        dag.add_task(task)
        class_task.set_upstream(task) 

    do_dag(dag, concurrent, refresh)

    return 0


def grand_multi(args):

    run_grand_multi(
        genomes=args.genomes,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh,
        job_type=args.job_type,
    )


def add_grand_multi_args(parser):

    parser.add_argument("genomes", metavar='FILE', type=str,
        help="Input the genome list.")
    parser.add_argument("--concurrent", metavar="INT", type=int, default=10,
        help="Maximum number of jobs concurrent  (default: 10).")
    parser.add_argument("--refresh", metavar="INT", type=int, default=30,
        help="Refresh time of log in seconds  (default: 30).")
    parser.add_argument("--job_type", choices=["sge", "local"], default="local",
        help="Jobs run on [sge, local]  (default: local).")
    parser.add_argument("--work_dir", metavar="DIR", type=str, default=".",
        help="Work directory (default: current directory).")
    parser.add_argument("--out_dir", metavar="DIR", type=str, default=".",
        help="Output directory (default: current directory).")

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
attention:
    grand.py multi genomes.list
File format：
name    genome

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_grand_multi_args(parser)
    args = parser.parse_args()
    grand_multi(args)


if __name__ == "__main__":
    main()
