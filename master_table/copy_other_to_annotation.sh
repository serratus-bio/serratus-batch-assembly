#for accession in `cat master_table.accessions.txt`
#do

copyjob () {
	accession=$1
	aws s3 cp s3://serratus-public/assemblies/other/$accession.coronaspades/$accession.coronaspades.gene_clusters.checkv_filtered.fa.darth.tar.gz      s3://serratus-public/assemblies/annotations/$accession.fa.darth.tar.gz
	aws s3 cp s3://serratus-public/assemblies/other/$accession.coronaspades/$accession.coronaspades.gene_clusters.checkv_filtered.fa.serraplace.tar.gz s3://serratus-public/assemblies/annotations/$accession.fa.serraplace.tar.gz
	aws s3 cp s3://serratus-public/assemblies/other/$accession.coronaspades/$accession.coronaspades.gene_clusters.checkv_filtered.fa.serratax.tar.gz   s3://serratus-public/assemblies/annotations/$accession.fa.serratax.tar.gz
	aws s3 cp s3://serratus-public/assemblies/other/$accession.coronaspades/$accession.coronaspades.gene_clusters.checkv_filtered.fa.serratax.final    s3://serratus-public/assemblies/annotations/$accession.fa.serratax.final
}
export -f copyjob
echo "disabled this script as new annotations might get overwritten"
#cat master_table.accessions.txt  | parallel -j15 "copyjob {}"

#done

