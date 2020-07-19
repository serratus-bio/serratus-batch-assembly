placejob () {
	accession=$1
	mkdir $accession.serraplace
        cd $accession.serraplace
        /place.sh -g -d ../../assemblies/$accession.fa
	cd ..
	mv $accession.serraplace/assign/best_longest.readable.per_query.tsv $accession.best_longest.readable.per_query.tsv
        tar -zcvf $accession.serraplace.tar.gz $accession.serraplace
	aws s3 cp $accession.serraplace.tar.gz s3://serratus-public/assemblies/annotations/ --acl public-read
	rm -Rf $accession.serraplace
}
export -f placejob
cat ~/serratus-batch-assembly/master_table/master_table.accessions.txt | parallel -j15 "placejob {}"
