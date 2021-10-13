#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, get_version
from dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_ltr_args


LOG = logging.getLogger(__name__)

LOG = logging.getLogger(__name__)
__version__ = "1.1.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_ltr_finder_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["ltr_finder"] = {
        "version": get_version(SOFTWARE_VERSION["ltr_finder"]),
        "option": "-C -w 0"
    }
    ltr_finder_task = Task(
        id="ltr_finder",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={ltr_finder}:$PATH
#ltr_finder {genome} -C -w 0 >{prefix}.ltr_finder.tsv
{script}/ltr_finder2gff.py {prefix}.ltr_finder.tsv >{prefix}.ltr_finder.gff
{script}/get_gff2fa.py {prefix}.ltr_finder.gff -g {genome} -tp all >{prefix}.ltr_finder.fasta
cp {prefix}.ltr_finder.tsv {prefix}.ltr_finder.gff {prefix}.ltr_finder.fasta {out_dir}
""".format(ltr_finder=LTR_FINDER_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return ltr_finder_task, option, os.path.join(work_dir, "%s.ltr_finder.tsv" % prefix)


def create_ltr_finder_parallel_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["LTR_FINDER_parallel"] = {
        "version": get_version(SOFTWARE_VERSION["LTR_FINDER_parallel"]),
        "option": "default"
    }
    ltr_finder_task = Task(
        id="LTR_FINDER_parallel",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={LTR_FINDER_parallel}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
LTR_FINDER_parallel -seq {prefix}.fasta -threads {thread} -harvest_out
mv {prefix}.fasta.finder.combine.gff3 {prefix}.ltr_finder.gff3
mv {prefix}.fasta.finder.combine.scn {prefix}.ltr_finder.scn
cp {prefix}.ltr_finder.gff3 {prefix}.ltr_finder.scn {out_dir}
""".format(LTR_FINDER_parallel=LTR_FINDER_parallel,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            thread=thread,
            out_dir=out_dir
        )
    )

    return ltr_finder_task, option, os.path.join(work_dir, "%s.ltr_finder.scn" % prefix)


def create_ltrharvest_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["ltrharvest"] = {
        "version": get_version(SOFTWARE_VERSION["ltrharvest"]),
        "option": "default"
    }
    ltrharvest_task = Task(
        id="ltrharvest",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={reasonaTE}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
gt suffixerator -db {prefix}.fasta -indexname {prefix}.index -tis -suf -lcp -des -ssp -sds -dna
gt ltrharvest -index {prefix}.index > {prefix}.ltrharvest.tsv
cp {prefix}.ltrharvest.tsv {out_dir}
rm {prefix}.index.*
""".format(reasonaTE=REASONATE_BIN,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return ltrharvest_task, option, os.path.join(work_dir, "%s.ltrharvest.tsv" % prefix)


def create_ltr_retriever_task(prefix, genome, ltr_finder, ltrharvest, thread, job_type, work_dir, out_dir):

    option = {}
    option["ltr_retriever"] = {
        "version": get_version(SOFTWARE_VERSION["ltr_retriever"]),
        "option": "default"
    }

    retriever_task = Task(
        id="ltr_retriever",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={ltr_retriever}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
cat {ltr_finder} {ltrharvest} >{prefix}.rawLTR.scn
LTR_retriever -genome {prefix}.fasta -inharvest {prefix}.rawLTR.scn -threads {thread}
{script}/scn2gff.py {prefix}.fasta.retriever.all.scn >{prefix}.ltr_retriever.gff
{script}/get_gff2fa.py {prefix}.ltr_retriever.gff -g {prefix}.fasta -tp all >{prefix}.ltr_retriever.fasta
mv {prefix}.fasta.retriever.all.scn {prefix}.ltr_retriever.scn
cp {prefix}.ltr_retriever.scn {prefix}.ltr_retriever.gff {prefix}.ltr_retriever.fasta {out_dir}
""".format(ltr_retriever=LTR_RETRIEVER_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            ltr_finder=ltr_finder,
            ltrharvest=ltrharvest,
            thread=thread,
            out_dir=out_dir
        )
    )

    return retriever_task, option, os.path.join(work_dir, "%s.ltr_retriever.fasta" % prefix)


def run_ltr(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "ltr_finder": "01_ltr_finder",
        "ltrharvest": "02_ltrharvest",
    }
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))

    dag = DAG("grand_ltr")
    ltr_finder_task, option, ltr_finder = create_ltr_finder_parallel_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["ltr_finder"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(ltr_finder_task)

    ltrharvest_task, option, ltrharvest = create_ltrharvest_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["ltrharvest"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(ltrharvest_task)

    retriever_task, option, retriever = create_ltr_retriever_task(
        prefix=prefix,
        genome=genome,
        ltr_finder=ltr_finder,
        ltrharvest=ltrharvest,
        thread=thread,
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(retriever_task)
    retriever_task.set_upstream(ltr_finder_task)
    retriever_task.set_upstream(ltrharvest_task)

    do_dag(dag, concurrent, refresh)

    return options, retriever



def ltr(args):

    options = run_ltr(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_ltr.json"), "w") as fh:
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

    parser = add_ltr_args(parser)
    args = parser.parse_args()
    ltr(args)


if __name__ == "__main__":
    main()
