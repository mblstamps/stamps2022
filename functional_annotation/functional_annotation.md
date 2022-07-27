Hands on Tutorial: Functional Annotation
=============

Mihai gave a great conceptual introduction to functional annotation (LINK).
During this lesson, we'll get some hands-on experience with functional annotation.
We're going to use the same metagenome that we used in the [assembly and binning tutorial](https://github.com/mblstamps/stamps2022/blob/main/assembly_and_binning/tutorial_assembly_and_binning.md), but we'll start from the assembly and bins generated from the full set of reads. 
Since we only worked with a subset of reads, we'll have to download those files.


Let's start by creating a directory for today's tutorial.

```
cd ~
mkdir functional_annotation
cd functional_annotation
```

Let's also create a conda environment and install the software programs we'll need.

```
mamba create -n annot -c conda-forge -c bioconda -c defaults prodigal=2.6.3 kofamscan=1.3.0
conda activate annot
```

Here, we install two programs that we'll use to do functional annotation.
The first, [`prodigal`](https://github.com/hyattpd/Prodigal), is the field-standard tool for annotating open reading frames (ORFs) in bacterial and archaeal sequences. 
It doesn't do gene or ortholog annotation, it only identifies open reading frames and outputs the sequences.
The second, `kofamscan`, does ortholog annotation on amino acid sequences, providing [KEGG annotations](https://www.genome.jp/kegg/) for each sequence.

> Note about KEGG: KEGG is a proprietary resource with a paid-access model. 
> The fees KEGG charges support curation and tool development.
> While the KEGG database is available online, it's not fully programmitcally available unless you pay for it.
> However, _representations_ of the data _can_ be reproduced and provided for free. 
> kofamscan, while produced by KEGG, makes KEGG annotations available to the broader community by distributing hidden markov models of KEGG orthologs. 
> HMMs are representations, so it's a nice workaround.


Let's download the full assembly for SRR8859675.

```
wget -O SRR8859675_final_contigs.fasta https://osf.io/aq2nk/download
```


## Predicting open reading frames from bacterial and/or archaeal contigs

Once we have a contig that we're interested in annotating, the first thing we need to do is identify the open reading frames.
[ORFs](https://www.genome.gov/genetics-glossary/Open-Reading-Frame) are nucleotides that occur between start and stop codons in DNA sequences.
ORFs often encode proteins, so extracting ORFs gets us one step closer to identifying the functional content in sequences of interest.

We'll use prodigal to extract open reading frames.
As stated above, prodigal is the field-standard for ORF identification and extraction in bacterial and archaeal genomes.

Run prodigal with the `-h` flag to see what options are available

```
prodigal -h
```

```
Usage:  prodigal [-a trans_file] [-c] [-d nuc_file] [-f output_type]
                 [-g tr_table] [-h] [-i input_file] [-m] [-n] [-o output_file]
                 [-p mode] [-q] [-s start_file] [-t training_file] [-v]

         -a:  Write protein translations to the selected file.
         -c:  Closed ends.  Do not allow genes to run off edges.
         -d:  Write nucleotide sequences of genes to the selected file.
         -f:  Select output format (gbk, gff, or sco).  Default is gbk.
         -g:  Specify a translation table to use (default 11).
         -h:  Print help menu and exit.
         -i:  Specify FASTA/Genbank input file (default reads from stdin).
         -m:  Treat runs of N as masked sequence; don't build genes across them.
         -n:  Bypass Shine-Dalgarno trainer and force a full motif scan.
         -o:  Specify output file (default writes to stdout).
         -p:  Select procedure (single or meta).  Default is single.
         -q:  Run quietly (suppress normal stderr output).
         -s:  Write all potential genes (with scores) to the selected file.
         -t:  Write a training file (if none exists); otherwise, read and use
              the specified training file.
         -v:  Print version number and exit.
```

There are a few flags that are useful here.
First, we see `-a`, which will allow us to write out amino acid sequences (translated) ORFs.
`-d` allows us to also save the nucleotide sequences.
Lastly, `-p` let's us tell prodigal that we're working with a metagenome.
By default, prodigal assumes we are working with a single genome. 
In this mode, it will study the sequences we give it to try to better learn how to predict ORFs for that genome. 
By telling it we are working with a metagenome (which holds sequences from many different genomes) it will use pre-calculated training files to guide its predictions.

```
prodigal -i SRR8859675_final_contigs.fasta -d SRR8859675_final_contigs.fna -a SRR8859675_final_contigs.faa -p meta -o SRR8859675_final_contigs.gbk
```

Let's take a look at the output amino acid sequences.

```
less SRR8859675_final_contigs.faa
```


## Ortholog annotation with kofamscan

Now that we have predicted amino acid sequences, we can try to determine their function by using ortholog annotation.
Orthologs are genes which evolved from a common ancestral gene by speciation that usually have retained a similar function in different species [source](https://www.sciencedirect.com/topics/biochemistry-genetics-and-molecular-biology/orthology).

As with most things in bioinformatics, there are many ways to annotate amino acid sequences. 
We will be using kofamscan, a tool that uses hidden markov models built from KEGG orthologs to assign KEGG ortholog numbers to new amino acid sequences. 
Hidden markov models work well for protein annotation because they weight the importance of each amino acid in determining the final assignment. 
Look at the sequence logo figure below.

![](https://i.imgur.com/5Cq8Tiy.png)

This figure is a logo depicting the PFAM HMM for rpsG. 
rpsG encodes 30S ribosomal protein S7, and it is a highly conserved protein. 
The HMM was built from hundreds of rpsG protein sequences. 
At each position of the protein, the logo depicts the liklihood of seeing a specific amino acid. 
The larger the amino acid is in the logo, the more likely it is to be observed at that position. 
In positions where no amino acid is visible, it is less important which amino acid occurs there. 
This encoding is more flexible than something like Hamming distance or BLAST because it incorporates biological importance of amino acid positionality. 
This approach works well on novel amino acid sequences that are not closely related to anything currently housed in databases.

`kofamscan` is a tool released by the KEGG that includes HMMs built from each KEGG ortholog. 
Using `kofamscan`, we can assign KEGG orthologs to our amino acid sequences. 
This allows us to take advantage of KEGG pathway information.

`kofamscan` is run by using the `exec_annotation` command:

```
exec_annotation --help
```

`kofamscan` needs a few database files in order to run.
Let's download them.

```
wget ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz      # download the ko list 
wget ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz # download the hmm profiles
```

The first file is the KEGG orthlog (KO) list.
The second file is the HMM profiles for the KOs.

We also have to unzip and untar the relevant files:
```
gunzip ko_list.gz
tar xf profiles.tar.gz
```

kofamscan runs using a config file. 
Using nano, build a config file that looks like this:

```
nano config.yaml
```

```
# Path to your KO-HMM database
# A database can be a .hmm file, a .hal file or a directory in which
# .hmm files are. Omit the extension if it is .hal or .hmm file
profile: ./profiles

# Path to the KO list file
ko_list: ko_list

# Path to an executable file of hmmsearch
# You do not have to set this if it is in your $PATH
# hmmsearch: /usr/local/bin/hmmsearch

# Path to an executable file of GNU parallel
# You do not have to set this if it is in your $PATH
# parallel: /usr/local/bin/parallel

# Number of hmmsearch processes to be run parallelly
cpu: 8
```
You might notice the `$PATH` variable above. We didn't get to cover what this special variable is in a Unix-like environment, but it can be useful to know about. The PATH variable holds all the locations (directories) our command line will automatically search when looking for a program we try to run. If interested in more about this and how to modify our PATH, you can find more about it [here](https://cac-staff.github.io/swc-bash-lesson/j05-hpc.html) 
**Challenge**
How many lines contain computer-readable information in this config file?

<details>
  <summary>Challenge Answer</summary>
    Three. Every other line is commented out.
</details>

Let's run the actual annotation command now.
```
exec_annotation -f mapper --config config.yaml -o SRR8859675_final_contigs_kofamscan.txt SRR8859675_final_contigs.faa
```

Look at the results:

```
less SRR8859675_final_contigs_kofamscan.txt 
```

## Visualizing the output

```
mamba create -n keggdecoder python=3.6 pip
conda activate keggdecoder
pip install KEGGDecoder==1.2.2
```

```
KEGG-decoder -i SRR8859675_final_contigs_kofamscan.txt -o kegg_decoder_out --vizoption static
```

When this is done running, you'll have a file named `kegg_decoder_out.svg`. 
You can open this in jupyter notebook or transfer it to your local computer using a program like `scp`.
We've recreated the visual below so you can look at it!

![](https://i.imgur.com/kB5CuIK.png)

**Challenge**
How would this visualization change if we had run `kofamscan` on MAGS vs. on the metagenome assembly?

<details>
  <summary>Challenge Answer</summary>
    Assuming every contig was binned, we would still see all of the functions represented in the plot, but we would have a row for each MAG. The functions would be spread out across the organisms.
</details>

## Other annotation tools

The next steps in any workflow will depend on the goal of your study.


We showed you how to use kofamscan, in part because KEGG offers a rich set of knowledge to integrate with (pathways, metabolites, organisms, etc). 
However, there are other tools and databases that you can use to perform annotation. 
We include some below that we like, but keep in mind that this is not an exhaustive list!


| Tool | Annotations | Reference |
| -------- | -------- | -------- |
| kofamscan     | KEGG   |   [ref](https://academic.oup.com/bioinformatics/article/36/7/2251/5631907)   |
| emapper | COG/NOG, KEGG, CAzy, EC, GO | [ref](https://academic.oup.com/mbe/article/38/12/5825/6379734)|
| bakta | gene names  (not orthologs) | [ref](https://www.microbiologyresearch.org/content/journal/mgen/10.1099/mgen.0.000685)|
| prokka | gene names (not orthologs) | [ref](https://academic.oup.com/bioinformatics/article/30/14/2068/2390517) |

