echo "gathering accessions"
#bash gather_coronaspades_ver.sh > list_latest_ver.txt 	
echo "minimap2 of contigs to cov5"
#bash minimap2_contigs.sh
echo "making master table"
python master_table.py
