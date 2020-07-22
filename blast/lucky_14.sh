#!/bin/bash

#rm -f lucky_14.fa
#for f in `cat ../lists/lucky_14.txt`
#do
#	aws s3 cp s3://serratus-public/assemblies/contigs/$f.coronaspades.checkv_filtered.fa .
#	cat $f.coronaspades.checkv_filtered.fa >> lucky_14.fa
#done


f=~/lucky_14/lucky_14.fa
#\time $HOME/ncbi-blast-2.10.1+/bin/blastn -db $HOME/blastdb/nt -query $f -num_threads 32 -outfmt 6 > $f.blast-fmt6 
\time $HOME/ncbi-blast-2.10.1+/bin/blastx -db $HOME/blastdb/nr -query $f -num_threads 16 -outfmt 6 > $f.blastx-fmt6 
