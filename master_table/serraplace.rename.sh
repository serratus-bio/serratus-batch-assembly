placejob () {
	accession=$1
	good_file_exists=$(aws s3 ls s3://serratus-public/assemblies/annotations/$accession.fa.serraplace.tar.gz)
	bad_file_exists=$(aws s3 ls s3://serratus-public/assemblies/annotations/$accession.serraplace.tar.gz)
	if test -n "$good_file_exists"
	then
		# clean up bad file
		aws s3 rm s3://serratus-public/assemblies/annotations/$accession.serraplace.tar.gz
		return
	fi
	if test -n "$bad_file_exists"
	then
		aws s3 mv s3://serratus-public/assemblies/annotations/$accession.serraplace.tar.gz s3://serratus-public/assemblies/annotations/$accession.fa.serraplace.tar.gz
	fi
}
export -f placejob
cat ~/serratus-batch-assembly/master_table/master_table.accessions.txt | parallel -j15 "placejob {}"
