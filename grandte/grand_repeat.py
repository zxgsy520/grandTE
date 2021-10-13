#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, mkdir, get_version
from dagflow import DAG, Task, ParallelTask, do_dag
from grandte.parser import add_repeat_args


LOG = logging.getLogger(__name__)

LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def create_RepeatMasker_task(prefix, genome, lib, thread, job_type, work_dir, out_dir, species="human"):

    option = {}
    option["RepeatMasker"] = {
        "version": get_version(SOFTWARE_VERSION["RepeatMasker"]),
        "option": "default"
    }
    if lib:
        species = ""
        engine = ""
        lib = "-lib %s" % lib
    else:
        species = "-species %s" % species
        engine = "-engine nhmmer"
        lib = ""
    task = Task(
        id="RepeatMasker",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s -V " % thread,
        script="""
export PATH={masker}:$PATH
cut -d " " -f1 {genome} >{prefix}.fasta
RepeatMasker -nolow -no_is -gff -norna {species}\\
    -parallel {thread} {engine} {lib} \\
    -dir ./ {prefix}.fasta
mv {prefix}.fasta.out.gff {prefix}.RepeatMasker.gff
{script}/filter_masker.py {prefix}.RepeatMasker.gff > {prefix}.RepeatMasker_new.gff
{script}/stat_transposon.py {prefix}.fasta -g {prefix}.RepeatMasker.gff3 --sample {prefix} >{prefix}.stat_transposon.tsv
cp {prefix}.RepeatMasker.gff3 {prefix}.stat_transposon.tsv {out_dir}
cp {prefix}.RepeatMasker_new.gff {out_dir}/{prefix}.RepeatMasker.gff
""".format(masker=REPEATMASKER_BIN,
            script=SCRIPTS,
            species=species,
            engine=engine,
            lib=lib,
            thread=thread,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return task, option, os.path.join(out_dir, "%s.RepeatMasker.gff3" % prefix), os.path.join(out_dir, "%s.stat_transposon.tsv" % prefix)


def create_RepeatModeler_task(prefix, genome, thread, job_type, work_dir, out_dir):

    option = {}
    option["RepeatModeler"] = {
        "version": get_version(SOFTWARE_VERSION["RepeatModeler"]),
        "option": "default"
    }
    task = Task(
        id="RepeatModeler",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s -V " % thread,
        script="""
#export PATH={masker}:$PATH
export PATH={modeler}:$PATH
export PERL5LIB={masker_perl_lib}:$PERL5LIB
BuildDatabase -name {prefix} -engine rmblast  {genome}
RepeatModeler -pa {thread} -database {prefix} -engine rmblast
mv {prefix}-families.fa {prefix}.RepeatModeler.fasta
cp {prefix}.RepeatModeler.fasta {out_dir}
""".format(masker=REPEATMASKER_BIN,
            masker_perl_lib=MASKER_PERL_LIB,
            modeler=REPEATMODELER_BIN,
            thread=thread,
            prefix=prefix,
            genome=genome,
            out_dir=out_dir
        )
    )

    return task, option, os.path.join(work_dir, "%s.RepeatModeler.fasta" % prefix)


def run_repeat(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh, species="human", lib=""):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "masker": "01_RepeatMasker",
        "modeler": "02_RepeatModeler",
    }
    options = {
        "software": OrderedDict(),
        "database": OrderedDict()
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))

    dag = DAG("grand_repeat")
    masker_task, option, masked_gff, masked_tsv = create_RepeatMasker_task(
        prefix=prefix,
        genome=genome,
        lib=lib,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["masker"]),
        out_dir=out_dir,
        species=species,
    )
    options["software"].update(option)
    dag.add_task(masker_task)

    modeler_task, option, modeler = create_RepeatModeler_task(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["modeler"]),
        out_dir=out_dir
    )
    options["software"].update(option)
    dag.add_task(modeler_task)
    do_dag(dag, concurrent, refresh)

    return options, masked_tsv


def repeat(args):

    options, masked_tsv = run_repeat(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grand_repeat.json"), "w") as fh:
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

    parser = add_repeat_args(parser)
    args = parser.parse_args()
    repeat(args)


if __name__ == "__main__":
    main()
