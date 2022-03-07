# grandTE
Genomic transposon prediction analysis

Availability
------------

grandTE is available for Linux and MacOS platforms.

Building Requirements
---------------------

* Python 2.7 or 3.5+ (with setuptools package installed)
* matplotlib
* numpy
* scipy

Local building (without installation)
-------------------------------------

You may use the package locally without system installation.
To get and compile the latest git version, run:

    git clone https://github.com/zxgsy520/grandTE
    cd grandTE
    chmod 755 grandte.py

Then, grandTE will be available as:

    python grandte.py


Required Batabase
---------------------
* [prosite.dat](https://ftp.expasy.org/databases/prosite/prosite.dat)

Third-party
-----------
grandTE package includes some third-party software:
* [transposon_annotation_tools](https://github.com/DerKevinRiehl/transposon_annotation_tools)
* [blastn](https://ftp.ncbi.nlm.nih.gov/blast/executables/legacy.NOTSUPPORTED/)
* [GMATA](https://sourceforge.net/projects/gmata/)
* [TRF](https://github.com/Benson-Genomics-Lab/TRF)
* [muscle](http://www.drive5.com/muscle/downloads.htm)
* [mdust](https://github.com/lh3/mdust)
* [MITE-Hunter](http://target.iplantcollaborative.org/mite_hunter.html)
* [mustv2](http://www.healthinformaticslab.org/supp/resources.php)
* [mitetracker](https://github.com/INTABiotechMJ/MITE-Tracker)
* [MiteFinderII](https://github.com/jhu99/miteFinder)
* [ps_scan](https://ftp.expasy.org/databases/prosite/ps_scan/)
* [ltr_finder](https://github.com/xzhub/LTR_Finder)
* [LTR_FINDER_parallel](https://github.com/oushujun/LTR_FINDER_parallel)
* [ltrharvest](http://genometools.org/license.html)
* [LTR_retriever](https://github.com/oushujun/LTR_retriever)
* [SINE-Finder]()
* [SINE_scan](https://github.com/maohlzj/SINE_Scan)
* [HelitronScanner](http://bo.csam.montclair.edu/helitronscanner/)
* [cd-hit](http://weizhong-lab.ucsd.edu/cd-hit/)
* [RepeatModeler](https://github.com/Dfam-consortium/RepeatModeler)
* [Repeatmasker](http://www.repeatmasker.org/)
* [TEclass](https://github.com/zxgsy520/TEclass) 
* 说明：安装RepeatModeler和Repeatmasker可以先使用TEclass(TEclass软件比较老，可以用最新的一些分类软件试试)对Repeat数据库里面未分类的重复序列进行分类.

References
-----------
Wang, Xuewen, and Le Wang. “GMATA: An Integrated Software Package for Genome-Scale SSR Mining, Marker Development and Viewing.” Frontiers in plant science vol. 7 1350. 13 Sep. 2016, [doi:10.3389/fpls.2016.01350](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5020087/)

Ge, Ruiquan et al. “MUSTv2: An Improved De Novo Detection Program for Recently Active Miniature Inverted Repeat Transposable Elements (MITEs).” Journal of integrative bioinformatics vol. 14,3 20170029. 10 Aug. 2017, [doi:10.1515/jib-2017-0029](https://pubmed.ncbi.nlm.nih.gov/28796642/)

Macko-Podgórni, Alicja et al. “A Global Landscape of Miniature Inverted-Repeat Transposable Elements in the Carrot Genome.” Genes vol. 12,6 859. 3 Jun. 2021, [doi:10.3390/genes12060859](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8227079/)

Crescente, Juan Manuel et al. “MITE Tracker: an accurate approach to identify miniature inverted-repeat transposable elements in large genomes.” BMC bioinformatics vol. 19,1 348. 3 Oct. 2018, [doi:10.1186/s12859-018-2376-y](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6171319/)

Ye, Congting et al. “detectMITE: A novel approach to detect miniature inverted repeat transposable elements in genomes.” Scientific reports vol. 6 19688. 22 Jan. 2016, [doi:10.1038/srep19688](https://pubmed.ncbi.nlm.nih.gov/26795595/)

Hu, Jialu et al. “MiteFinderII: a novel tool to identify miniature inverted-repeat transposable elements hidden in eukaryotic genomes.” BMC medical genomics vol. 11,Suppl 5 101. 20 Nov. 2018, [doi:10.1186/s12920-018-0418-y](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6245586/)

Ou, Shujun, and Ning Jiang. “LTR_FINDER_parallel: parallelization of LTR_FINDER enabling rapid identification of long terminal repeat retrotransposons.” Mobile DNA vol. 10 48. 12 Dec. 2019, [doi:10.1186/s13100-019-0193-0](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6909508/)

Ellinghaus, David et al. “LTRharvest, an efficient and flexible software for de novo detection of LTR retrotransposons.” BMC bioinformatics vol. 9 18. 14 Jan. 2008, [doi:10.1186/1471-2105-9-18](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2253517/)

Ou, Shujun, and Ning Jiang. “LTR_retriever: A Highly Accurate and Sensitive Program for Identification of Long Terminal Repeat Retrotransposons.” Plant physiology vol. 176,2 (2018): 1410-1422. [doi:10.1104/pp.17.01310](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5813529/)

Wenke, Torsten et al. “Targeted identification of short interspersed nuclear element families shows their widespread existence and extreme heterogeneity in plant genomes.” The Plant cell vol. 23,9 (2011): 3117-28. [doi:10.1105/tpc.111.088682](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3203444/)

Mao, Hongliang, and Hao Wang. “SINE_scan: an efficient tool to discover short interspersed nuclear elements (SINEs) in large-scale genomic datasets.” Bioinformatics (Oxford, England) vol. 33,5 (2017): 743-745. [doi:10.1093/bioinformatics/btw718](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5408816/)

Xiong, Wenwei, and Chunguang Du. “Mining hidden polymorphic sequence motifs from divergent plant helitrons.” Mobile genetic elements vol. 4,5 1-5. 30 Oct. 2014, [doi:10.4161/21592543.2014.971635](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4588551/)

Fu, Limin et al. “CD-HIT: accelerated for clustering the next-generation sequencing data.” Bioinformatics (Oxford, England) vol. 28,23 (2012): 3150-2. [doi:10.1093/bioinformatics/bts565](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3516142/)

Flynn, Jullien M et al. “RepeatModeler2 for automated genomic discovery of transposable element families.” Proceedings of the National Academy of Sciences of the United States of America vol. 117,17 (2020): 9451-9457. [doi:10.1073/pnas.1921046117](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7196820/)

Chen, Nansheng. “Using RepeatMasker to identify repetitive elements in genomic sequences.” Current protocols in bioinformatics vol. Chapter 4 (2004): Unit 4.10. [doi:10.1002/0471250953.bi0410s05](https://pubmed.ncbi.nlm.nih.gov/18428725/)
