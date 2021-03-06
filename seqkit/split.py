#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import argparse
import logging
from multiprocessing import Pool


from .common import fofn2list, mkdir, touch, get_seq_format
from .FastaReader import open_fasta
from .FastqReader import open_fastq
from .common import __author__, __version__, __email__


LOG = logging.getLogger(__name__)


def split_record(records, mode, number, out_fmt, out_bed=False, out_dir="split", minlen=0):
    """

    :param records:
    :param mode:
    :param number:
    :param out_fmt:
    :param out_bed:
    :param out_dir:
    :return:
    """
    r = []
    n = 1

    while True:

        out_filename = os.path.join(out_dir, out_fmt.format(num=n))

        out = open(out_filename, "w")
        beds = []

        count = 0

        for record in records:
            id = record.id
            length = len(record)
            if length <= minlen:
                continue
            out.write(str(record) + "\n")

            if out_bed:
                beds.append("%s\t1\t%s\n" % (id, length))

            if mode == "length":
                count += length
            else:
                count += 1

            if count >= number:
                break

        out.close()

        if out_bed:
            with open(out_filename + ".bed", "w") as fh:
                fh.write("%s\n" % "\n".join(beds))

        if count == 0:
            os.remove(out_filename)  # remove the empty file
            if out_bed:
                os.remove(out_filename + ".bed")
        else:
            r.append(out_filename)

        if count < number:
            break

        n += 1

    return r


def split_file(filename, index, mode, number, out_dir="split", minlen=0):
    """

    :param filename:
    :param index:
    :param mode:
    :param number:
    :param out_dir:
    :return:
    """
    r = []

    LOG.info("%s process %r" % (index, filename))
    prefix, fmt = get_seq_format(filename)

    if fmt == "fasta":
        r = split_record(open_fasta(filename), mode=mode, number=number,
                         out_fmt="%s.{num}.fasta" % prefix, out_bed=True,
                         out_dir=out_dir, minlen=minlen)
    elif fmt == "fastq":

        if prefix.endswith(".R1"):
            prefix = "%s_{num}.R1.fastq" % prefix.rstrip("R1")
        elif prefix.endswith(".R2"):
            prefix = "%s_{num}.R2.fastq" % prefix.rstrip("R2")
        else:
            prefix = "%s_{num}.fastq" % prefix

        r = split_record(open_fastq(filename), mode=mode, number=number,
                         out_fmt=prefix, out_bed=False, out_dir=out_dir, minlen=minlen)
    else:
        LOG.info("??? seq format")  # will raise exception in get_seq_format

    return r


def seq_split(filenames, mode, num, output_dir, concurrent=1, minlen=0):
    """
    split fasta files, use multiprocess for parallel
    :param filenames: a list of fasta files
    :param mode: length or number
    :param num:
    :param output_dir: output directory
    :param concurrent: see -h
    :return:
    """
    assert mode in ["number", "length"]
    num = int(num)

    output_dir = mkdir(output_dir)
    split_list = os.path.join(output_dir, "split_list")
    done = os.path.join(output_dir, "split_done")

    # avoid rerun
    if os.path.exists(done):
        LOG.info("%r exists, pass this step; if you want to rerun, delete the file" % done)
        return fofn2list(split_list)

    # for multiprocessing
    pool = Pool(processes=concurrent)
    results = []

    LOG.info("Split '{filenames}' by sequence {mode} =~ {num} per file".format(**locals()))

    file_num = len(filenames)

    for i, file in enumerate(filenames):
        index = "%s/%s" % (i+1, file_num)
        results.append(pool.apply_async(split_file, (file, index, mode, num, output_dir, minlen)))

    pool.close()
    pool.join()

    file_list = []

#    for i, r in enumerate(results):
    for r in results:
        file_list += r.get()

    with open(split_list, "w") as fh:
        fh.write("\n".join(file_list))

    touch(done)
    return file_list


def split_args(parser):

    parser.add_argument("seq", metavar="FILES", nargs="+", help="files, '.gz' is accepted")
    parser.add_argument("-m", "--mode", choices=["number", "length"], required=True, help="split by number or length")
    parser.add_argument("-n", "--number", type=int, required=True, metavar="INT", help="the value of mode")
    parser.add_argument("-o", "--output_dir", default="split", metavar="DIR", help="output directory")
    parser.add_argument("-c", "--concurrent", metavar='INT', type=int, default=1, help="number of concurrent process")

    return parser


def split(args):

    seq_split(args.seq, args.mode, args.number, args.output_dir, args.concurrent)


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                   description="""
Split sequence files(fastA/Q)

version: %s
contact: %s <%s>\
""" % (__version__, " ".join(__author__), __email__))

    parser = split_args(parser)
    args = parser.parse_args()
    split(args)


if __name__ == "__main__":
    main()

