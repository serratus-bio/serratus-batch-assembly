
structurejob () {
	accession=$1
	assembly=assemblies/$accession.fa
	hmm=/darth/Pfam-A.SARS-CoV-2.hmm

	# try two methods: transeq and getorf

	for flavor in ".transeq" ".orfs"
	do
		if [[ "$flavor" == ".orfs" ]]
		then
			input=genome_structure/$accession.orfs.fa
			getorf -minsize 300 $assembly $input
		else
			input=genome_structure/$accession.transeq.fa
			transeq -frame 6 $assembly $input
		fi
		sto=genome_structure/$accession"$flavor".sto
		tbl=genome_structure/$accession"$flavor".tbl
		domtbl=genome_structure/$accession"$flavor".domtbl
		hmmout=genome_structure/$accession"$flavor".hmmsearch_stdout
		hmmsearch --cut_ga -A $sto --tblout $tbl --domtblout $domtbl -o $hmmout $hmm $input

	done
}
export -f structurejob
cat ~/serratus-batch-assembly/master_table/master_table.accessions.txt  | parallel -j 15  "structurejob {}"
