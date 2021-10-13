#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, get_version
from dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_mite_args


LOG = logging.getLogger(__name__)

LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_mite_hunter_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["blastn"] = {
        "version": get_version(SOFTWARE_VERSION["blastn"]),
        "option": "default"
    }
    option["muscle"] = {
        "version": get_version(SOFTWARE_VERSION["muscle"]),
        "option": "default"
    }
    option["mdust"] = {
        "version": get_version(SOFTWARE_VERSION["mdust"]),
        "option": "default"
    }
    option["MITE-Hunter"] = {
        "version": "2011.11",
        "option": "-n 20 -P 1.0 -S 12345678 -c 24"
    }

    mite_hunter_task = Task(
        id="mite_hunter",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s -V " % thread,
        script="""
export PATH={blastn}:{muscle}:$PATH
export PATH={mdust}:{mite_hunter}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
MITE_Hunter_manager.pl -i {prefix}.fasta -g {prefix} \\
-n 20 -P 1.0 -S 12345678 -c 24
cat *_singlet.fa > {prefix}.mite_hunter.fasta
cp {prefix}.mite_hunter.fasta {out_dir}
rm -rf {prefix}*
""".format(blastn=BLAST_BIN,
            muscle=MUSCLE_BIN,
            mdust=MDUST_BIN,
            mite_hunter=MITE_HUNTER_BIN,
            prefix=prefix,
            genome=genome,
            work_dir=work_dir,
            out_dir=out_dir
        )
    )

    nucmer_task = Task(
        id="nucmer",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s " % thread,
        script="""
export PATH={nucmer}:$PATH
if [ -s {out_dir}/{prefix}.mite_hunter.fasta ] ; then
    nucmer --maxmatch --nosimplify -g 200 -c 50 -l 25 -t {thread} -p {prefix} {out_dir}/{prefix}.mite_hunter.fasta {genome}
    show-coords {prefix}.delta -rlo -L 45 >{prefix}.coords
    {script}/coords2gff.py {prefix}.coords >{prefix}.mite_hunter.gff3
else
    touch {prefix}.mite_hunter.gff3
fi
cp {prefix}.mite_hunter.gff3 {out_dir}
""".format(nucmer=NUCMER_BIN,
            script=SCRIPTS,
            prefix=prefix,
            genome=genome,
            thread=thread,
            work_dir=work_dir,
            out_dir=out_dir
        )
    )

    nucmer_task.set_upstream(mite_hunter_task)

    return mite_hunter_task, nucmer_task, option, os.path.join(out_dir, "%s.mite_hunter.gff3" % prefix)


def create_mustv2_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["mustv2"] = {
        "version": get_version(SOFTWARE_VERSION["mustv2"]),
        "option": "default"
    }
    mustv2_task = Task(
        id="mustv2",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s -V " % thread,
        script="""
export PATH={reasonaTE}:$PATH
mkdir -p temp
cut -d " " -f1 {genome} >{prefix}.fasta

if [ ! -e {prefix}.mustv2.tsv ]; then
    mustv2 {prefix}.fasta {prefix}.mustv2.tsv temp
fi

cp {prefix}.mustv2.tsv {out_dir}
rm -rf temp
""".format(reasonaTE=REASONATE_BIN,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return mustv2_task, option, os.path.join(work_dir, "%s.mustv2.tsv" % prefix)



def create_mitetracker_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["mitetracker"] = {
        "version": get_version(SOFTWARE_VERSION["mitetracker"]),
        "option": "default"
    }
    mitetracker_task = Task(
        id="mitetracker",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={reasonaTE}:$PATH
mkdir results
cut -d " " -f1 {genome} >{prefix}.fasta
mitetracker -g {prefix}.fasta -j jobName -w {thread}
cp results/jobName/all.fasta {prefix}.mitetracker.fasta
cp results/jobName/all.gff3 {prefix}.mitetracker.gff3
cp {prefix}.mitetracker.fasta {prefix}.mitetracker.gff3 {out_dir}
#rm -rf results
""".format(reasonaTE=REASONATE_BIN,
            prefix=prefix,
            genome=genome,
            thread=thread,
            out_dir=out_dir
        )
    )

    return mitetracker_task, option, os.path.join(work_dir, "%s.mitetracker.gff3" % prefix)


def create_miteFinderII_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["miteFinderII"] = {
        "version": get_version(SOFTWARE_VERSION["miteFinderII"]),
        "option": "default"
    }
    miteFinderII_task = Task(
        id="miteFinderII",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={reasonaTE}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
miteFinderII -input {prefix}.fasta -output {prefix}.miteFinderII.tsv
cp {prefix}.miteFinderII.tsv {out_dir}
""".format(reasonaTE=REASONATE_BIN,
            prefix=prefix,
            genome=genome,
            thread=thread,
            out_dir=out_dir
        )
    )

    return miteFinderII_task, option, os.path.join(work_dir, "%s.miteFinderII.tsv" % prefix)


def create_merge_mite_task(prefix, genome, mite_hunter, mitetracker, mustv2, miteFinderII, job_type, work_dir, out_dir):

    task = Task(
        id="merge_mite",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp 1",
        script="""
{script}/merge_mite.py --gffs {mite_hunter} {mitetracker} \\
    --tsvs {mustv2} {miteFinderII} >{prefix}.MITE.gff3
{script}/get_gff2fa.py {prefix}.MITE.gff3 -g {genome} -tp MITE >{prefix}.MITE.fasta
cp {prefix}.MITE.gff3 {prefix}.MITE.fasta {out_dir}
""".format(script=SCRIPTS,
            mite_hunter=mite_hunter,
            mitetracker=mitetracker,
            mustv2=mustv2,
            miteFinderII=miteFinderII,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return task, os.path.join(out_dir, "%s.MITE.fasta" % prefix)


def run_mite(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "mite_hunter": "01_mite_hunter",
        "mustv2": "02_mustv2",
        "mitetracker": "03_mitetracker",
        "miteFinderII": "04_miteFinderII",
    }
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))

    dag = DAG("grand_mite")
    mite_hunter_task, nucmer_task, option, mite_hunter = create_mite_hunter_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["mite_hunter"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(mite_hunter_task)
    dag.add_task(nucmer_task)

    mustv2_task, option, mustv2 = create_mustv2_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["mustv2"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(mustv2_task)

    mitetracker_task, option, mitetracker = create_mitetracker_task(
        prefix=prefix,
        genome=genome,
        thread=thread*2,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["mitetracker"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(mitetracker_task)

    miteFinderII_task, option, miteFinderII = create_miteFinderII_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["miteFinderII"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(miteFinderII_task)
    
    merge_task, mite = create_merge_mite_task(
        prefix=prefix,
        genome=genome,
        mite_hunter=mite_hunter,
        mitetracker=mitetracker,
        mustv2=mustv2,
        miteFinderII=miteFinderII,
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir
    )
    dag.add_task(merge_task)
    merge_task.set_upstream(nucmer_task)
    merge_task.set_upstream(mustv2_task)
    merge_task.set_upstream(mitetracker_task)
    merge_task.set_upstream(miteFinderII_task)

    do_dag(dag, concurrent, refresh)

    return options, mite


def mite(args):

    run_mite(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_mite.json"), "w") as fh:
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

    parser = add_mite_args(parser)
    args = parser.parse_args()
    mite(args)


if __name__ == "__main__":
    main()
