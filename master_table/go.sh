echo "copy from s3"
#bash copy.sh # this one is to be run in ~/master_table
echo "gathering accessions"
#bash gather_coronaspades_ver.sh > list_latest_ver.txt 	
echo "get bgc_cov"
# bash bgc_cov.sh #this one is to be run in ~/master_table
echo "minimap2 of contigs to cov5"
#bash minimap2_contigs.sh
echo "making master table"
python master_table.py

# to provide data:
# bash copy_other_to_annotation.sh
# python extract_pfam.py
