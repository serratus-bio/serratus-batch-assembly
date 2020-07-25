
testjob () {
	accession=$1
	bgcstats=data/$accession.coronaspades/$accession.coronaspades.bgc_statistics.txt
	ls -l $bgcstats
	if [[ $(grep -i rdrp $bgcstats) ]]
	then
		geneclusters=data/$accession.coronaspades/$accession.coronaspades.gene_clusters.fa
		geneclustersaa=data/$accession.coronaspades/$accession.coronaspades.gene_clusters.aa
		transeq -frame 6 $geneclusters $geneclustersaa
		rdrpsto=data/$accession.coronaspades/$accession.rdrp.sto
		rdrpa2m=data/$accession.coronaspades/$accession.rdrp.a2m
		hmmsearch --cut_ga -A $rdrpsto rdrp.hmm $geneclustersaa
		esl-reformat a2m $rdrpsto > $rdrpa2m
	fi
}
export -f testjob
cat ~/serratus-batch-assembly/master_table/master_table.accessions.txt  | parallel -j 15  "testjob {}"
