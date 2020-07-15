find data/ -name "*.bgc_statistics.txt" | 
	parallel -j10 \
	"python ~/serratus-batch-assembly/stats/bgc_parse_and_extract.py {}"
