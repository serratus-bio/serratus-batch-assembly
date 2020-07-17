aws s3 ls s3://serratus-public/assemblies/other/ --recursive | grep darth.tar.gz | tee darth.txt
python darth.accessions.py | sort > darth.accessions.txt
awk -F, '{print $1}' master_table.csv | sort  > master_table.accessions.txt
comm -3 darth.accessions.txt master_table.accessions.txt > darth.tosubmit.txt
