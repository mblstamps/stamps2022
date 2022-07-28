# <a name="first">Strain-level analyses with ParSNP (STAMPS 2022)</a>
========

This tutorial is to go over how to use ParSNP for strain-level analyses of genomes. The first dataset is a MERS coronavirus outbreak dataset involving 49 isolates. The second dataset is a selected set of 31 Streptococcus pneumoniae genomes. For reference, both of these datasets should run on modestly equipped laptops in a few minutes or less.

   1) <a name="part3e1">Example 1: 49 MERS Coronavirus genomes </a>
   
      * Download genomes: 
         * `mkdir parsnp_demo1`
         * `cd parsnp_demo1`
         * `wget https://github.com/marbl/harvest/raw/master/docs/content/parsnp/mers49.tar.gz` [download](https://github.com/marbl/harvest/raw/master/docs/content/parsnp/mers49.tar.gz)
         * `tar -xvf mers49.tar.gz`
    
      * Run parsnp with default parameters 
      
         parsnp -r ./mers49/England1.fna -d ./mers49 -c
         
      * Command-line output 

        ![merscmd](https://github.com/marbl/harvest/raw/master/docs/content/parsnp/run_mers.cmd1.png?raw=true)

      * Visualize with Gingr [download](https://github.com/marbl/harvest/raw/master/docs/content/parsnp/run_mers.gingr1.ggr)
      
        ![mers1](https://github.com/marbl/harvest/raw/master/docs/content/parsnp/run_mers.gingr1.png?raw=true)

      * Configure parameters
      
         - 95% of the reference is covered by the alignment. This is <100% mainly due to a 1kbp unaligned region from 26kbp to 27kbp.
         - To force alignment across large collinear regions, use the `-C` maximum distance between two collinear MUMs::
         
            ./parsnp -r ./mers49/England1.fna -d ./mers49 -C 2000 -c
            
      * Visualize again with Gingr :download:`GGR <run_mers.gingr2.ggr>`
      
         - By adjusting the `-C` parameter, this region is no longer unaligned, boosting the reference coverage to 97%.

        ![mers2](https://github.com/marbl/harvest/raw/master/docs/content/parsnp/run_mers.gingr2.png?raw=true)
        
      * Zoom in with Gingr for nucleotide view of region
      
         - On closer inspection, a large stretch of N's in Jeddah isolate C7569 was the culprit
         
        ![mers3](https://github.com/marbl/harvest/raw/master/docs/content/parsnp/run_mers.gingr3.png?raw=true)
         
      * Inspect Output:
      
         * Multiple alignment: :download:`XMFA <runm1.xmfa>` 
         * SNPs: :download:`VCF <runm1.vcf>`
         * Phylogeny: :download:`Newick <runm1.tree>`
 
   2) <a name="part3e2">Example 2: 31 Streptococcus pneumoniae genomes </a>
   
     --Download genomes:
   * `cd $HOME`
   * `mkdir parsnp_demo2`
   * `cd parsnp_demo2`
   *  `wget https://github.com/marbl/harvest/raw/master/docs/content/parsnp/strep31.tar.gz`
   *  `tar -xvf strep31.tar.gz`
    
     --Run parsnp:
      
    parsnp -r ./strep31/NC_011900.fna -d ./strep31 -p 8

     --Force inclusion of all genomes (-c):
      
    parsnp -r ./strep31/NC_011900.fna -d ./strep31 -p 8 -c

     --Enable recombination detection/filter (-x):
      
    parsnp -r ./strep31/NC_011900.fna -d ./strep31 -p 8 -c -x

     --Inspect Output:
      
         * Multiple alignment: parsnp.xmfa
         * Phylogeny: parsnp.tree


This last step requires you to download software and is to highlight the ability to inspect strain-level differences within genomes assembled from metagenomic samples.

1) Use AliView 

    * Download AliView:

    [https://ormbunkar.se/aliview/downloads/)

    * Download MFA file:

    wget https://obj.umiacs.umd.edu/stamps2019/aliview.input.mfa

    * Open AliView
      
    * Load MFA file:

    File->Open File

