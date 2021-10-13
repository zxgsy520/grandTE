#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os.path
import shutil
import logging
import argparse

from grandte.config import *
from grandte.common import check_path, check_paths, mkdir, get_version
from grandte.grand_mite import run_mite
from grandte.grand_ltr import run_ltr
from grandte.grand_sine import run_sine
from grandte.grand_tir import run_tir
from grandte.grand_helitron import run_helitron
from grandte.grand_repeat import run_repeat
from grandte.parser import add_all_args
from dagflow import DAG, Task, do_dag


LOG = logging.getLogger(__name__)
__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def build_database(prefix, fasts, thread, job_type, work_dir, out_dir, concurrent, refresh):

    fasts = check_paths(fasts)

    option = {}
    option["cd-hit"] = {
        "version": get_version(SOFTWARE_VERSION["cd-hit"]),
        "option": "default"
    }

    dag = DAG("build_database")
    cdhit_task = Task(
        id="cdhit",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp %s" % thread,
        script="""
export PATH={cdhit}:$PATH
cat {fasts} >TE.fasta
cd-hit-est -i TE.fasta -c 0.90 -p 1 -o {prefix}_TE_id.fa -d 0 -g 1 -M 500 -T {thread}
{script}/fa2maskerdb.py {prefix}_TE_id.fa >{prefix}_TE.lib
""".format(cdhit=CDHIT_BIN,
            script=SCRIPTS,
            prefix=prefix,
            fasts=" ".join(fasts),
            thread=thread,
            out_dir=out_dir
        )
    )
    dag.add_task(cdhit_task)

    do_dag(dag, concurrent, refresh)

    return option, os.path.join(work_dir, "%s_TE.lib" % prefix)


def class_te(tes, job_type, work_dir, out_dir, concurrent, refresh):

    tes = check_paths(tes)

    dag = DAG("class_te")
    class_task = Task(
        id="class",
        work_dir=work_dir,
        type=job_type,
        option="-pe smp 1",
        script="""
{script}/class_stat_transposon.py {tes}
cp *_transposon.tsv {out_dir}
""".format(script=SCRIPTS,
            tes=" ".join(tes),
            out_dir=out_dir
        )
    )
    dag.add_task(class_task)

    do_dag(dag, concurrent, refresh)

    return 0


def run_grand_all(prefix, genome, thread, job_type, work_dir, out_dir, concurrent, refresh):

    genome = check_path(genome)
    work_dir = mkdir(work_dir)
    out_dir = mkdir(out_dir)

    work_dict = {
        "mit": "01_mit",
        "ltr": "02_ltr",
        "sine": "03_sine",
        "tir": "04_tir",
        "helitron": "05_helitron",
        "database": "database",
        "repeat": "06_repeat",
    }
    for k, v in work_dict.items():
        mkdir(os.path.join(work_dir, v))
        if v == "database":
            continue
        mkdir(os.path.join(out_dir, v))
    fasts = []

    options, mite = run_mite(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["mit"]),
        out_dir=os.path.join(out_dir, work_dict["mit"]),
        concurrent=concurrent,
        refresh=refresh
    )
    fasts.append(mite)

    option_new, ltr = run_ltr(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["ltr"]),
        out_dir=os.path.join(out_dir, work_dict["ltr"]),
        concurrent=concurrent,
        refresh=refresh
    )
    fasts.append(ltr)
    options["software"].update(option_new["software"])

    option_new, sine = run_sine(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["sine"]),
        out_dir=os.path.join(out_dir, work_dict["sine"]),
        concurrent=concurrent,
        refresh=refresh
    )
    fasts.append(sine)
    options["software"].update(option_new["software"])

    option_new, tir = run_tir(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["tir"]),
        out_dir=os.path.join(out_dir, work_dict["tir"]),
        concurrent=concurrent,
        refresh=refresh
    )
    fasts.append(tir)
    options["software"].update(option_new["software"])

    option_new, helitron = run_helitron(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["helitron"]),
        out_dir=os.path.join(out_dir, work_dict["helitron"]),
        concurrent=concurrent,
        refresh=refresh
    )
    options["software"].update(option_new["software"])
    fasts.append(helitron)

    option, TE_lib = build_database(
        prefix=prefix,
        fasts=fasts,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["database"]),
        out_dir=os.path.join(work_dir, work_dict["database"]),
        concurrent=concurrent,
        refresh=refresh
    )
    options["software"].update(option)

    tes = []
    option_new, masked_tsv = run_repeat(
        prefix=prefix,
        genome=genome,
        thread=thread,
        job_type=job_type,
        work_dir=os.path.join(work_dir, work_dict["repeat"]),
        out_dir=os.path.join(out_dir, work_dict["repeat"]),
        concurrent=concurrent,
        refresh=refresh,
        lib=TE_lib
    )
    options["software"].update(option_new["software"])
    tes.append(masked_tsv)

    class_te(tes=tes,
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir,
        concurrent=concurrent,
        refresh=refresh
    )

    return options


def grand_all(args):

    options = run_grand_all(
        prefix=args.prefix,
        genome=args.genome,
        thread=args.thread,
        job_type=args.job_type,
        work_dir=args.work_dir,
        out_dir=args.out_dir,
        concurrent=args.concurrent,
        refresh=args.refresh
    )
    with open(os.path.join(args.out_dir, "grandte.json"), "w") as fh:
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

    parser = add_grandte_args(parser)
    args = parser.parse_all_args()
    grand_all(args)


if __name__ == "__main__":
    main()
