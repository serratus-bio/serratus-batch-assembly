rm -f genome_structure.data.py
for domtbl in `ls -1 genome_structure/*.transeq.domtbl`
do
	python genome_structure.parser.py $domtbl >> genome_structure.data.py
done
