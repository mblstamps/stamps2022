Hands on tutorial: Metagenome Assembly & Binning Workflow
=============



Today we will execute a *de novo* shotgun metagenome workflow.
What makes a good metagenome workflow? 
As with everything we've covered so far, it depends :)

But we have to start somewhere!
We find that it's generally a good idea to do a "default" workflow.
This allows you to start getting to know your data quickly, and to get **a result** quickly.
After you have results from the default workflow, you can critically assess whether they make sense in light of your biological problem or whether you need to use different methods to answer your question.
You can also measure attrition of information and determine if you need to do something about it.

There are a lot of steps in a default *de novo* metagenome workflow. 
Below we have a diagram of each step one would generally want to take ([source](https://github.com/metagenome-atlas/atlas)).

![](https://i.imgur.com/AElQa79.png)

There are 17 steps! Each of which requires a different tool. 
That's a lot of tools! 

Instead of orchestrating these 17 tools ourselves, we can put an automated workflow to work for us to do this. 
We chose to use the [ATLAS](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-020-03585-4) workflow because...it works. 
Which is actually a sort of high bar for stringing 17 tools together!

## Instance hygiene

Metagenomics workflows can take up quite a bit of space. 
We want to make sure that we have enough space and compute power on our instances to execute the whole thing. 

We need three things to run a workflow: hard drive space, RAM, and CPUs. 
+ **hard drive space** is physical, persistent storage. 
We write our files to disk for long term storage
+ **RAM** is working memory. 
It temporarily stores all the information that your computer needs to work right that minute. 
Some tools need to load all of your data into RAM in order to work with it.
Assembly is one of these steps -- to assemble something, you need at minimum the amount of RAM as you have in gigabytes of data.
+ **CPUs** are the electronic circuitry within a computer that carries out the instructions of a computer program by performing the basic arithmetic, logic, controlling, and input/output (I/O) operations specified by the instructsion (see wikipedia [article here](https://en.wikipedia.org/wiki/Central_processing_unit)).

Log into your jetstream instance using `ssh` or the jupyter lab url.

If you don't have access to a jetstream instance, you can use this Pangeo binder link instead: [![Binder](https://aws-uswest2-binder.pangeo.io/badge_logo.svg)](https://aws-uswest2-binder.pangeo.io/v2/gh/taylorreiter/stamps2022-binder/main)  

When you have a remote computer up and running, open a terminal.
Let's check the amount of hard drive space we have. 
From your bash prompt, run:

```
df -h .
```

You should see an output like this:

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        58G   15G   44G  25% /
```

You need at least 10G of space on your instance. 
If you don't have that much, put up a pink sticky and a helper will come around to help remove files. 

Let's also take a look at how much ram we have available:

```
free -mh
```

and you'll see something like this:
```
               total        used        free      shared  buff/cache   available
Mem:            29Gi       894Mi        27Gi       1.0Mi       1.2Gi        28Gi
Swap:             0B          0B          0B
```

And the amount of CPUs:

```
nproc
```

Which should return:

```
8
```

Ok! We now have an idea of how much compute is available to us. 
In general, it's really hard to know how much of each resource you need for each tool before you run it. 
You may be able to google around for this information, but you will also develop this intuition over time as you run more tools. 
We have enough compute to execute our tutorial because we are working with a subsampled dataset. 

The last bit of instance hygiene we need to take care of is making sure that we all have the right channels, or package managers, enabled for conda. 
We'll go over this in detail, but essentially if our computers don't know where to look to install software, or if they look at the wrong location first, things will go awry. 

```
conda activate
```

```
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
```

## Getting started with ATLAS

We'll organize ourselves as if we're starting a brand new project. 

```
cd ~
mkdir atlas_workflow
cd atlas_workflow/
```

We also need to install atlas to get this metagenome party started. We'll do that with this code, and we'll go over what it all means in our evening session.

```
mamba create -y -n atlas metagenome-atlas=2.9.1
conda activate atlas
```

Ok! We now have atlas installed. 
Let's checked that our installation worked by running atlas.

```
atlas
```

You should see a help message that looks like this:

```
Usage: atlas [OPTIONS] COMMAND [ARGS]...

  ATLAS - workflows for assembly, annotation, and genomic binning of
  metagenomic and metatranscriptomic data.

  For updates and reporting issues, see: https://github.com/metagenome-
  atlas/atlas

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  download     download reference files (need ~50GB)
  init         prepare configuration file and sample table for atlas run
  init-public  Prepare atlas run from public data from SRA
  run          run atlas main workflow
```

## Retrieving the data

We will be working with two metagenomes from Woods Hole!
The samples come from the Trunk River lagoon in Falmouth (just a short ways up the road!) which has large amounts of biomass and which experiences periodic bright yellow microbial blooms, typically associated with disturbances to the ecosystem ([source](https://environmentalmicrobiome.biomedcentral.com/articles/10.1186/s40793-019-0348-0?_ga=2.190106795.160855720.1658156183-1639102303.1656704578)).
These metagenomes were sampled from human-made disturbances that caused blooms.
The accession numbers are SRR8859675 and SRR8859678. 
Each sample has about ~1 GB of data, and it would take too long to run atlas on the entire dataset (~4 hours).

For this tutorial, we subsampled the SRR8859675 to the first 1 million paired-end reads, and we will be working with this subsampled data. 

First, let's download our data.

```
mkdir data
wget -O data/SRR8859675_R1.fq.gz https://osf.io/mhr9y/download
wget -O data/SRR8859675_R2.fq.gz https://osf.io/8usdv/download 
```

We can check that the download was successful by listing the files with `ls`:

```
ls -lh data
```

We see that we now have about 160 MB of data.


```
-rw-rw-r-- 1 stamps2022 stamps2022 40M Jul 24 18:22 SRR8859675_R1.fq.gz
-rw-rw-r-- 1 stamps2022 stamps2022 49M Jul 24 18:22 SRR8859675_R2.fq.gz
```

## Configuring atlas

We now need to tell atlas where our data is. 
We do this with the `atlas init` command. 
We'll also tell atlas that we're working with metagenome data, and that we want atlas to do assembly with megahit.
(you could definitely use a different assembler! We're using megahit here because it uses the least ram and takes the least amount of time.)

```
atlas init data/ --assembler megahit --data-type metagenome
```

You should see output that looks like this:

```
[Atlas] INFO: Configuration file written to /home/stamps2022/atlas_workflow/config.yaml
        You may want to edit it using any text editor.
[Atlas] INFO: I inferred that _R1 and _R2 distinguish paired end reads.
[Atlas] INFO: Found 1 samples
```

In running this command, atlas has created a configuration file for itself using the path of our data. 
Let's take a look at this "config" file to see what decisions atlas is making under the hood. 
Note, here we are choosing to use megahit because it uses substantially less memory that (meta)spades.

```
less config.yaml
```

The first thing we see is that atlas would prefer that we have 32 GB of RAM for most tools, and 250 GB of RAM for assembly, and more than 6 threads for assembly. 
Sorry atlas, not gonna happen!!! 
We need to edit this file to set atlas straight about our resources. 
We will use nano to do this.

```
nano config.yaml
```

We need to edit these numbers so they reflect our actual resources. Make sure the top of your file looks like this:

```
########################
# Execution parameters
########################
# threads and memory (GB) for most jobs especially from BBtools, which are memory demanding
threads: 8
mem: 28

# threads and memory for jobs needing high amount of memory. e.g GTDB-tk,checkm or assembly
large_mem: 28
large_threads: 8
assembly_threads: 8
assembly_memory: 28
simplejob_mem: 10
```

To exit, type `ctrl X` type `y`, and press `enter`. This will write the changes we made to our file. 

Let's also look at the samples file and make sure that atlas got it right. 

```
cat samples.tsv
```

Everything looks good here! Atlas successfully realized that we are working with one sample with paired end reads.

## Running atlas!

Now that everything is set up, we could type `atlas run` and it would orchestrate everything for us. We're not going to do that though. We're going to run each step of the pipeline in pieces and look at the output. We're also going to skip the database download step, because it takes too much disk space and RAM to build the databases for annotation. 

### Quality Control

Let's start with quality control. We'll use the `-n` flag first, which tells atlas to run a `--dryrun`. This tells you everything that is about to be run but doesn't actually run it. (It also checks to be sure that your config files are formatted properly!)

```
atlas run qc -n
```

We see a bunch of green and gold output. This is good! Let's take a closer look at what this means:

```
Job stats:
job                          count    min threads    max threads
-------------------------  -------  -------------  -------------
apply_quality_filter             1              8              8
build_decontamination_db         1              8              8
build_qc_report                  1              1              1
calculate_insert_size            1              4              4
combine_insert_stats             1              1              1
combine_read_counts              1              1              1
combine_read_length_stats        1              1              1
deduplicate_reads                1              8              8
download_atlas_files             2              1              1
finalize_sample_qc               1              1              1
get_read_stats                   5              4              4
initialize_qc                    1              4              4
qc                               1              1              1
qcreads                          1              1              1
run_decontamination              1              8              8
write_read_counts                1              1              1
total                           21              1              8

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Let's run the QC command while we discuss what is happening (it takes about 7 minutes to run):

```
atlas run qc
```

Atlas is automated using a tool called [Snakemake](https://snakemake.readthedocs.io/en/stable/). 
We love snakemake :) - it does the thing, and orchestrates all the things for you. 
If this sounds appealing to you, here is a [tutorial](https://angus.readthedocs.io/en/2019/snakemake_for_automation.html) on how to use snakemake.

We see that 21 different steps are wrapped by the QC command. 
These steps control contamination, run quality control (erroneous k-mers, adapters, etc.), and generate reports about the different steps that are run. 
As each rule runs, we see green snakemake text alerting us to which step is running, and we see white text from the stdout ("standard output") from each tool that is run. 
Some of the longest steps are downloading and installing all of the software that's needed - it's using conda to do this, note!

When atlas is finished with QC, we'll see:

```
Complete log: .snakemake/log/2022-07-21T125750.640127.snakemake.log
ATLAS finished
The last rule shows you the main output files
```

If we list the files with `ls -FC`, you'll see we have many more files and directories:

```
SRR8859675/  config.yaml  data/  databases/  finished_QC  logs/  ref/  reports/  samples.tsv  stats/
```

Our results are located in the `SRR8859675/` folder.

```
ls SRR8859675/
```

And looking inside the folder in this folder:
```
ls SRR8859675/sequence_quality_control
```
We see:
```
SRR8859675_QC_R1.fastq.gz  SRR8859675_QC_se.fastq.gz                       contaminants  read_stats
SRR8859675_QC_R2.fastq.gz  SRR8859675_decontamination_reference_stats.txt  finished_QC
```

These are our quality controlled reads. We also see a file that says `finished_QC`. 
This is how atlas alerts us that it finished running all quality control steps.

**Challenge 1**

Look inside the contaminants folder. What contaminant was removed by atlas?

<details>
  <summary>Challenge Answer</summary>

To look inside the contaminants folder using the following command:
```
$ ls SRR8859675/sequence_quality_control/contaminants/
```
You'll see:
```
PhiX_R1.fastq.gz  PhiX_R2.fastq.gz  PhiX_se.fastq.gz
```
PhiX is the contaminant sequence that is removed by ATLAS by default
</details>



#### Rerunning atlas steps

Note that you can rerun `atlas run qc` and (as long as you succeeded the first time) atlas won't rerun anything! 
That's because atlas (and the snakemake tool its built on) tracks what's been done and won't rerun anything that has suceeded!

If you want to rerun the QC step, you can rename (or remove) the output of the atlas step, and rerun `atlas run qc`.

### Assembly

QC. Done. Yay! 
Now that our reads are cleaned up and we have removed contaminants, let's assemble. 
Again, let's do a dry run first to see what steps atlas will run. 

```
atlas run assembly -n
```

```
Would remove temporary output finished_QC
Job stats:
job                             count    min threads    max threads
----------------------------  -------  -------------  -------------
align_reads_to_final_contigs        1              8              8
assembly                            1              1              1
assembly_one_sample                 1              1              1
bam_2_sam_contigs                   1              4              4
build_assembly_report               1              1              1
calculate_contigs_stats             2              1              1
combine_contig_stats                1              1              1
convert_sam_to_bam                  1              4              4
do_not_filter_contigs               1              1              1
error_correction                    1              8              8
finalize_contigs                    1              1              1
get_contigs_from_gene_names         1              1              1
init_pre_assembly_processing        1              1              1
merge_pairs                         1              8              8
pileup                              1              8              8
predict_genes                       1              1              1
rename_contigs                      1              4              4
rename_megahit_output               1              1              1
run_megahit                         1              8              8
total                              20              1              8
```

Lots of things! Let's start the assembly and then we'll talk through these steps (takes ~8 min).

```
atlas run assembly
```

Megahit is the meat and potatoes of this pipeline. 
It orchestrates the assembly of our reads, generating long(er) contigs. 
(We ran it during the initial assembly tutorial, too.)

After the assembly is finished, the reads are mapped back to the assembly. 
This is good for quality control of our assembly (does our assembly fully capture the information in our reads?), and helps with downstream processes like binning.

The first step of annotation also occurs during the assembly phase. Here, the open reading frames (ORFs) are predicted. 

After these processes finish, we can take a look at the assembly and associated output files

```
ls SRR8859675/
```

In this directory, we see the file `finished_assembly`, as well as new folders for annotation, assembly, and sequence alignment. 

We can check the size of our assembly

```
ls -lh SRR8859675/assembly/
```

And take a look at the assembly itself

```
less SRR8859675/assembly/SRR8859675_final_contigs.fasta
```

Tons of contigs, most of them babies (#babycontigs).

**Challenge 2:** use a combination of `grep` and `wc` to count the number of contigs in our final assembly. 

<details>
  <summary>Challenge Answer</summary>
To find the number of contigs, grep for `>`, and then count the number of occurrences using `wc -l`.
```
grep ">" SRR8859675/assembly/SRR8859675_final_contigs.fasta | wc -l
```
```
1293
```
</details>


**Challenge 3:** explore the other output files in the assembly directory and subfolders. 
Find the file with more assembly stats and view it with `less`.

<details>
  <summary>Challenge Answer</summary>
    ```
    less -S SRR8859675/assembly/contig_stats/final_contig_stats.txt
    ```
</details>

### Binning


Now that we have an assembly, we want to bin it into bins (metagenome assembled genomes).

```
atlas run binning -n
```

```
Would remove temporary output finished_assembly
Job stats:
job                               count    min threads    max threads
------------------------------  -------  -------------  -------------
bam_2_sam_binning                     1              8              8
binning                               1              1              1
build_bin_report                      1              1              1
combine_bin_stats                     1              1              1
download_checkm_data                  1              1              1
get_bins                              1              1              1
get_contig_coverage_from_bb           1              1              1
get_maxbin_cluster_attribution        1              1              1
get_metabat_depth_file                1              8              8
get_unique_bin_ids                    2              1              1
get_unique_cluster_attribution        2              1              1
initialize_checkm                     1              1              1
maxbin                                1              8              8
merge_checkm                          1              1              1
metabat                               1              8              8
pileup_for_binning                    1              8              8
run_checkm_lineage_wf                 1              8              8
run_checkm_tree_qa                    1              1              1
run_das_tool                          1              8              8
total                                21              1              8
```

Let's get this running as we break down what's actually happening.

```
atlas run binning
```

Atlas does both binning and bin evaluation. 
We can see from the dry run that atlas uses many binners -- maxbin, metabat, concoct, and DAS tool. 
DAS tool combines the output of the other three binning tools, and summarizes their overlaps.

For bin evaluation, atlas runs CheckM. 
CheckM also assigns taxonomy, so a little bit of annotation happens in this step as well.

After a bit of time passes, we will see this error on the screen:

```
[Fri Jul 22 09:01:39 2022]
Error in rule run_checkm_lineage_wf:
    jobid: 34
    output: SRR8859675/binning/DASTool/checkm/completeness.tsv, SRR8859675/binning/DASTool/checkm/storage/tree/concatenated.fasta
    log: SRR8859675/logs/binning/DASTool/checkm.log (check log file(s) for error message)
    conda-env: /home/stamps2022/atlas_workflow/databases/conda_envs/a489c28d87eeb559bd025b7924d669bc
    shell:

        rm -r SRR8859675/binning/DASTool/checkm
        checkm lineage_wf 
            --file SRR8859675/binning/DASTool/checkm/completeness.tsv            
            --tmpdir /tmp             
            --tab_table             
            --quiet            
            --extension fasta             
            --threads 8             
            SRR8859675/binning/DASTool/bins             
            SRR8859675/binning/DASTool/checkm &> SRR8859675/logs/binning/DASTool/checkm.log

        (one of the commands exited with non-zero exit code; note that snakemake uses bash strict mode!)

Removing output files of failed job run_checkm_lineage_wf since they might be corrupted:
SRR8859675/binning/DASTool/checkm/storage/tree/concatenated.fasta
Shutting down, this might take some time.
Exiting because a job execution failed. Look above for error message
Note the path to the log file for debugging.
Documentation is available at: https://metagenome-atlas.readthedocs.io
Issues can be raised at: https://github.com/metagenome-atlas/atlas/issues
The code used to generate one or several output files has changed:
    To inspect which output files have changes, run 'snakemake --list-code-changes'.
    To trigger a re-run, use 'snakemake -R $(snakemake --list-code-changes)'.
The input used to generate one or several output files has changed:
    To inspect which output files have changes, run 'snakemake --list-input-changes'.
    To trigger a re-run, use 'snakemake -R $(snakemake --list-input-changes)'.
Complete log: .snakemake/log/2022-07-22T085856.769525.snakemake.log
[Atlas] CRITICAL: Command 'snakemake --snakefile /home/stamps2022/.conda/envs/atlas/lib/python3.8/site-packages/atlas/workflow/Snakefile --directory /home/stamps2022/atlas_workflow --jobs 8 --rerun-incomplete --configfile '/home/stamps2022/atlas_workflow/config.yaml' --nolock   --use-conda --conda-prefix /home/stamps2022/atlas_workflow/databases/conda_envs    --resources mem=27 mem_mb=28585 java_mem=23   --scheduler greedy  binning   ' returned non-zero exit status 1.
```

We see from the top of this message that snakemake is encountering an error.
Let's trouble shoot this error and figure out what happened.

In the error message, we see `&> SRR8859675/logs/binning/DASTool/checkm.log`. 
This is where the log message for this command is written.
Let's look at this error message and try and figure out what happened.


**Challenge 4**
Look at the stderror log message that was saved.
What do you think happened?
What process did you go through to figure out what happened?

```
less SRR8859675/logs/binning/DASTool/checkm.log
```

<details>
  <summary>Challenge Answer</summary>
It looks as though `pplacer` failed. 
We can copy the relevant parts of the error message and google them to see if anyone has encountered these problems before. 
If you google:

```
Uncaught exception: Sys_error("SRS049959/binning/DASTool/checkm/storage/tree/concatenated.pplacer.json: No such file or directory")
Fatal error: exception Sys_error("SRS049959/binning/DASTool/checkm/storage/tree/concatenated.pplacer.json: No such file or directory")
```

You might come upon [this](https://github.com/Ecogenomics/CheckM/issues/37) github issue. 

The key turns out to be that `Killed` message in the output above, which generally tells you that the computer ran out of memory at this step. This is because we "only" have 16 GB of RAM on these computers, and pplacer requires more.

</details>

Even though this failed with an error, quite a few steps finished.

If we do a dry run again, we can see that many of the steps completed:
```
atlas run binning -n
```

```
Would remove temporary output finished_assembly
Job stats:
job                      count    min threads    max threads
---------------------  -------  -------------  -------------
binning                      1              1              1
build_bin_report             1              1              1
combine_bin_stats            1              1              1
merge_checkm                 1              1              1
run_checkm_lineage_wf        1              2              2
run_checkm_tree_qa           1              1              1
total                        6              1              2

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Let's take a look and see how many bins were made.

```
ls SRR8859675/binning/DASTool/bins/
```

We see that there are two bins:
```
SRR8859675_metabat_1.fasta  SRR8859675_metabat_2.fasta
```

We'll work with these bins (or, rather, bins made from assembling and binning the full sample) more in future lessons.

## Other

### Annotation

We will be skipping these sections because they require large databases that take ~100 GB of hard drive space to build. 
However, on your samples, atlas would run gene annotation for each bin.
We'll also be going over annotation and functional annotation later this week with the assembly we created here, so stay tuned! 

## Other references

Don't like this pipeline? 
There are others that run in a very similar way! 
This [paper](https://www.sciencedirect.com/science/article/pii/S2001037021004931) does a great job of outlining different options. 
