#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, get_version
from dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_sine_args


LOG = logging.getLogger(__name__)

LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_sine_finder_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["sine_finder"] = {
        "version": get_version(SOFTWARE_VERSION["sine_finder"]),
        "option": "default"
    }
    sine_finder_task = Task(
        id="sine_finder",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={reasonaTE}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
sine_finder -V {prefix}.fasta
cat *-matches.fasta >{prefix}.sine_finder.tsv
cp {prefix}.sine_finder.tsv {out_dir}
""".format(reasonaTE=REASONATE_BIN,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    nucmer_task = Task(
        id="nucmer_sf",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s " % thread,
        script="""
export PATH={nucmer}:$PATH
if [ -s {out_dir}/{prefix}.sine_finder.tsv ] ; then
    nucmer --maxmatch --nosimplify -g 100 -c 40 -l 15 -t {thread} -p {prefix} {out_dir}/{prefix}.sine_finder.tsv {genome}
    show-coords {prefix}.delta -rlo -L 45 >{prefix}.coords
    {script}/coords2gff.py {prefix}.coords --source sine_finder --type SINE >{prefix}.sine_finder.gff3
else
    touch {prefix}.sine_finder.gff3
fi
cp {prefix}.sine_finder.gff3 {out_dir}
""".format(nucmer=NUCMER_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            thread=thread,
            out_dir=out_dir
        )
    )

    nucmer_task.set_upstream(sine_finder_task)

    return sine_finder_task, nucmer_task, option, os.path.join(work_dir, "%s.sine_finder.gff3" % prefix)


def create_sinescan_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["sinescan"] = {
        "version": get_version(SOFTWARE_VERSION["sinescan"]),
        "option": "default"
    }
    sinescan_task = Task(
        id="sinescan",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s -V " % thread,
        script="""
export PATH={reasonaTE}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
mkdir -p result
mkdir -p output
mkdir -p final
sinescan -s 123 -g {prefix}.fasta -o output -d result -z final
mv ./result/{prefix}.sine.fa {prefix}.sinescan.fasta
cp {prefix}.sinescan.fasta {out_dir}
rm -rf result output final
""".format(reasonaTE=REASONATE_BIN,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    nucmer_task = Task(
        id="nucmer_s",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s " % thread,
        script="""
export PATH={nucmer}:$PATH
if [ -s {out_dir}/{prefix}.sinescan.fasta ] ; then
    nucmer --maxmatch --nosimplify -g 100 -c 40 -l 15 -t {thread} -p {prefix} {out_dir}/{prefix}.sinescan.fasta {genome}
    show-coords {prefix}.delta -rlo -L 45 >{prefix}.coords
    {script}/coords2gff.py {prefix}.coords --source sinescan --type SINE >{prefix}.sinescan.gff3
else
    touch {prefix}.sinescan.gff3
fi
cp {prefix}.sinescan.gff3 {out_dir}
""".format(nucmer=NUCMER_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            thread=thread,
            out_dir=out_dir
        )
    )

    nucmer_task.set_upstream(sinescan_task)

    return sinescan_task, nucmer_task, option, os.path.join(work_dir, "%s.sinescan.gff3" % prefix)


def create_merge_sine_task(prefix, genome, sine_finder, sinescan, job_type, work_dir, out_dir):

    task = Task(
        id="merge_sine",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp 1",
        script="""
{script}/merge_mite.py --gffs {sine_finder} {sinescan} \\
    --locus SINE >{prefix}.SINE.gff3
{script}/get_gff2fa.py {prefix}.SINE.gff3 -g {genome} -tp SINE >{prefix}.SINE.fasta
cp {prefix}.SINE.gff3 {prefix}.SINE.fasta {out_dir}
""".format(script=SCRIPTS,
            sine_finder=sine_finder,
            sinescan=sinescan,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return task, os.path.join(out_dir, "%s.SINE.fasta" % prefix)


def run_sine(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "sine_finder": "01_sine_finder",
        "sinescan": "02_sinescan",
    }
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))

    dag = DAG("grand_ltr")
    sine_finder_task, nucmer_sf_task, option, sine_finder = create_sine_finder_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["sine_finder"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(sine_finder_task)
    dag.add_task(nucmer_sf_task)

    sinescan_task, nucmer_s_task, option, sinescan = create_sinescan_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["sinescan"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(sinescan_task)
    dag.add_task(nucmer_s_task)

    merge_task, sine = create_merge_sine_task(
        prefix=prefix,
        genome=genome,
        sine_finder=sine_finder,
        sinescan=sinescan,
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir
    )
    dag.add_task(merge_task)
    merge_task.set_upstream(nucmer_sf_task)
    merge_task.set_upstream(nucmer_s_task)

    do_dag(dag, concurrent, refresh)

    return options, sine


def sine(args):

    run_sine(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_sine.json"), "w") as fh:
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

    parser = add_sine_args(parser)
    args = parser.parse_args()
    sine(args)


if __name__ == "__main__":
    main()
