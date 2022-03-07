#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, check_paths, mkdir, get_version
from thirdparty.dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_trf_args


LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_trf_tasks(prefix, genomes, genome, thread, job_type,
                         work_dir, out_dir):

    option = {}
    option["trf"] = {
        "version": get_version(SOFTWARE_VERSION["trf"]),
        "option": "default"
    }
    prefixs = [os.path.basename(i) for i in genomes]
    id="trf"
    tasks = ParallelTask(
        id=id,
        work_dir="%s/{id}" % work_dir,
        type=job_type,
        option="-pe smp %s -V %s" % (thread, QUEUE),
        script="""
export PATH={trf}:$PATH
if [ ! -f "{{prefixs}}.2.7.7.80.10.50.500.dat" ];then
  trf {{genome}} 2 7 7 80 10 50 500 -f -d -h
fi
""".format(trf=TRF_BIN,
            ),
        genome=genomes,
        prefixs=prefixs,
    )

    join_task = Task(
        id="merge_trf",
        work_dir=work_dir,
        type="local",
        option="-pe smp 1 " ,
        script="""
cat {id}*/*.dat > {prefix}.TRF.dat
perl {script}/trf2gff3.pl {prefix}.TRF.dat {prefix}.TRF.gff3
perl {script}/maskedByGff.pl --mask_type softmask {prefix}.TRF.gff3 {genome} >{prefix}.TRFmasked.fasta
cp {prefix}.TRF.gff3 {prefix}.TRFmasked.fasta {out_dir}
""".format(id=id,
           script=SCRIPTS,
           genome=genome,
           prefix=prefix,
           out_dir=out_dir)
    )

    join_task.set_upstream(*tasks)

    return tasks, join_task, option, os.path.join(out_dir, "%s.TRF.gff3" % prefix)


def run_trf(prefix, genomes, genome, job_type, work_dir,
            out_dir, concurrent, refresh):

    genomes = check_paths(genomes)
    genome =  check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }

    dag = DAG("grand_trf")
    trf_tasks, trf_join, option, trf_gff = create_trf_tasks(
        prefix=prefix,
        genomes=genomes,
        genome=genome,
        thread=2,
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(*trf_tasks)
    dag.add_task(trf_join)

    do_dag(dag, concurrent, refresh)

    return options, trf_gff


def trf(args):

    options, trf_gff = run_trf(
        prefix=args.prefix,
        genomes=args.genomes,
        genome=args.genome,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_trf.json"), "w") as fh:
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

    parser = add_trf_args(parser)
    args = parser.parse_args()
    tir(args)


if __name__ == "__main__":
    main()
