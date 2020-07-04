#export BATCH_SIZE=20
#\time $HOME/ncbi-blast-2.10.1+/bin/blastn -db $HOME/blastdb/nt -query catA-v3.fa -num_threads 32 > catA-v3.blast 
for f in `ls split*.fa`
do
	\time $HOME/ncbi-blast-2.10.1+/bin/blastn -db $HOME/blastdb/nt -query $f -num_threads 32 -outfmt 6 > $f.blast-fmt6 
done
