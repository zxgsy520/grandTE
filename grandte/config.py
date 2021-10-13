
import os.path

from collections import OrderedDict

ROOT = "/export/personal1/zhangxg/my_develop/grandTE/v1.0.0/"
SCRIPTS = os.path.join(ROOT, "scripts")
TEMPLATES = os.path.join(ROOT, "templates")
BIN = os.path.join(ROOT, "grandte")


BLAST_BIN = "/export/personal/software/software/blast/v2.2.26/bin/"
MUSCLE_BIN = "/export/personal/software/software/muscle/v3.8.31/"
MDUST_BIN = "/export/personal/software/software/mdust/v0.0.1/"
MITE_HUNTER_BIN = "/export/personal/software/software/MITE-Hunter/latest/"
NUCMER_BIN = "/export/personal/software/software/mummer/v4.0.0/bin/"
REASONATE_BIN = "/export/personal/software/software/reasonaTE/v1.0.0/bin/"
LTR_FINDER_BIN = "/export/personal/software/software/LTR_Finder/v1.07/source/"
LTR_FINDER_parallel = "/export/personal/software/software/LTR_Finder/v1.1/"
LTR_RETRIEVER_BIN = "/export/personal/software/software/ltr_retriever/v2.9.0/bin/"
CDHIT_BIN = "/export/personal/software/software/cdhit/v4.8.1/"
REPEATMASKER_BIN = "/export/personal/software/software/RepeatMasker/v4.1.2.p1/bin/"
MASKER_PERL_LIB = "/export/personal/software/software/RepeatMasker/v4.1.2.p1/share/RepeatMasker/"
REPEATMODELER_BIN = "/export/personal/software/software/RepeatModeler/v2.0.2a/bin/"


SOFTWARE_VERSION = {
    "blastn":{
        "GETVER": "%s/blastn -version 2>&1| grep 'blastn'" % BLAST_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "2.2.31",
    },
    "muscle":{
        "GETVER": "%s/muscle -version 2>&1 |grep 'MUSCLE'" % MUSCLE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "3.8.31",
    },
    "mdust": {
        "GETVER": "ls %s/mdust 2>&1 |grep 'mdust'" % MDUST_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.0.0"
    },
    "mustv2": {
        "GETVER": "cat %s\mustv2 2>&1 |grep 'PRLSPTH2' |grep 'MUST_Pipe'" % REASONATE_BIN,
        "REGEXP": "\d+\-\d+\-\d+",
        "MINVER": "r2-4-002"
    },
    "mitetracker": {
        "GETVER": "ls %s\mitetracker" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.0.0"
    },
    "miteFinderII": {
        "GETVER": "export PATH=%s:$PATH;miteFinderII -version 2>&1 |grep 'VERSION'" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.0.006"
    },
    "ltr_finder": {
        "GETVER": "%s\ltr_finder -h 2>&1 |grep 'ltr_finder'" % LTR_FINDER_BIN,
        "REGEXP": "\d+\.\d+",
        "MINVER": "1.07"
    }, 
    "LTR_FINDER_parallel": {
        "GETVER": "%s\LTR_FINDER_parallel -h 2>&1 |grep 'Version:'" % LTR_FINDER_parallel,
        "REGEXP": "\d+\.\d+",
        "MINVER": "1.1"
    },
    "ltrharvest": { 
        "GETVER": "%s\gt ltrharvest -version 2>&1 |grep 'ltrharvest'" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.6.1"
    },
    "ltr_retriever": {
        "GETVER": "%s\LTR_retriever -h 2>&1 |grep 'LTR_retriever v'" % LTR_RETRIEVER_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "2.9.0"
    },
    "sine_finder": {
        "GETVER": "export PATH=%s:$PATH;sine_finder -v 2>&1 |grep 'VERSION'" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.0.1"
    },
    "sinescan": {
        "GETVER": "export PATH=%s:$PATH;sinescan -h 2>&1 cut -d '-' -f2 |grep '/SINE_Scan_process'" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.1.1"
    },
    "tirvish": {
        "GETVER": "export PATH=%s:$PATH;gt tirvish -version 2>&1 |grep 'GenomeTools'" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "1.6.1"
    },
    "helitronscanner": {
        "GETVER": "export PATH=%s:$PATH;helitronscanner -help 2>&1 |grep 'HelitronScanner'" % REASONATE_BIN,
        "REGEXP": "\d+\.\d+",
        "MINVER": "1.0"
    },
    "cd-hit": {
        "GETVER": "%s/cd-hit 2>&1 |grep 'CD-HIT version'" % CDHIT_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "4.8.1"
    },
    "RepeatMasker": {
        "GETVER": "%s/RepeatMasker -v 2>&1 |grep 'version'" % REPEATMASKER_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "4.1.1"
    },
    "RepeatModeler": {
        "GETVER": "%s/RepeatModeler -h 2>&1 |grep './RepeatModeler'" % REPEATMODELER_BIN,
        "REGEXP": "\d+\.\d+\.\d+",
        "MINVER": "2.0.2"
    },
}
