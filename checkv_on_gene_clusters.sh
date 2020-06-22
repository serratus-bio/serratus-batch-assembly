cd analysis

for contigs in `cat list_gene_clusters`
do
	aws s3 cp s3://serratus-public/assemblies/contigs/$contigs .
	contigs_filtered_filename=${contigs%.*}.checkv_filtered.fa

	checkv completeness $contigs out_checkv -t 4 -d $HOME/checkv-db-v0.6
	samtools faidx $contigs
	touch out_checkv/completeness.tsv 
	grep -f ../src/checkv_corona_entries.txt out_checkv/completeness.tsv | python ../src/extract_contigs.py $contigs $contigs_filtered_filename
	
	aws s3 cp $contigs_filtered_filename s3://serratus-public/assemblies/contigs/

	rm -Rf out_checkv
	rm -f $contigs
	rm -f $contigs.fai
	rm -f $contigs_filtered_filename

done

