aws s3 ls s3://serratus-public/assemblies/ --recursive | grep contigs.fa.mfc #| awk '{print $4}' |sed 's/\.fastq//g' |sort > find_non_downloaded.downloaded.txt
